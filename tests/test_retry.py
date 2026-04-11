"""Unit tests for the retry logic in the HTTP clients."""

from __future__ import annotations

import httpx
import pytest
import respx

from tradezero import TradeZeroClient
from tradezero.exceptions import NotFoundError, RateLimitError, ServerError

BASE = "https://webapi.tradezero.com/v1/api"
CREDS = {"api_key": "test-key", "api_secret": "test-secret"}


@respx.mock
def test_429_is_retried_then_succeeds() -> None:
    """A 429 response is retried; the next successful response is returned."""
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            return httpx.Response(429, json={"message": "rate limited"})
        return httpx.Response(200, json=[])

    respx.get(f"{BASE}/accounts").mock(side_effect=handler)
    client = TradeZeroClient(**CREDS)
    result = client.accounts.list_accounts()

    assert result == []
    assert call_count == 2


@respx.mock
def test_429_exhausts_all_retries_raises_rate_limit_error() -> None:
    """After all retries a persistent 429 raises RateLimitError."""
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(429, json={"message": "rate limited"})
    )
    client = TradeZeroClient(**CREDS)
    with pytest.raises(RateLimitError) as exc_info:
        client.accounts.list_accounts()
    assert exc_info.value.status_code == 429


@respx.mock
def test_500_is_retried_until_success() -> None:
    """A 500 response is retried; subsequent success is returned."""
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(500, text="Internal Server Error")
        return httpx.Response(200, json=[])

    respx.get(f"{BASE}/accounts").mock(side_effect=handler)
    client = TradeZeroClient(**CREDS)
    result = client.accounts.list_accounts()

    assert result == []
    assert call_count == 3


@respx.mock
def test_500_exhausts_retries_raises_server_error() -> None:
    """After all retries a persistent 500 raises ServerError."""
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(500, text="Internal Server Error")
    )
    client = TradeZeroClient(**CREDS)
    with pytest.raises(ServerError) as exc_info:
        client.accounts.list_accounts()
    assert exc_info.value.status_code == 500


@respx.mock
def test_404_is_not_retried() -> None:
    """404 Not Found must NOT be retried — it raises immediately."""
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(404, json={"message": "Account not found"})

    respx.get(f"{BASE}/account/MISSING").mock(side_effect=handler)
    client = TradeZeroClient(**CREDS)
    with pytest.raises(NotFoundError):
        client.accounts.get_account_details("MISSING")

    # 404 is not retryable — should be called exactly once
    assert call_count == 1


@respx.mock
def test_401_is_not_retried() -> None:
    """401 Unauthorized must NOT be retried."""
    from tradezero.exceptions import AuthenticationError

    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, json={"message": "Unauthorized"})

    respx.get(f"{BASE}/accounts").mock(side_effect=handler)
    client = TradeZeroClient(**CREDS)
    with pytest.raises(AuthenticationError):
        client.accounts.list_accounts()

    assert call_count == 1
