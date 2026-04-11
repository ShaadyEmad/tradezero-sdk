"""Unit tests for the retry logic in the HTTP clients."""

from __future__ import annotations

import httpx
import pytest
import respx

from tradezero import TradeZeroClient
from tradezero.exceptions import NotFoundError, RateLimitError, ServerError

BASE = "https://webapi.tradezero.com/v1/api"
CREDS = {"api_key": "test-key", "api_secret": "test-secret"}


def test_429_is_retried_then_succeeds() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            return httpx.Response(429, json={"message": "rate limited"})
        return httpx.Response(200, json=[])

    with respx.mock as mock:
        mock.get(f"{BASE}/accounts").mock(side_effect=handler)
        client = TradeZeroClient(**CREDS)
        result = client.accounts.list_accounts()

    assert result == []
    assert call_count == 2


def test_429_exhausts_all_retries_raises_rate_limit_error() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts").mock(
            return_value=httpx.Response(429, json={"message": "rate limited"})
        )
        client = TradeZeroClient(**CREDS)
        with pytest.raises(RateLimitError) as exc_info:
            client.accounts.list_accounts()
    assert exc_info.value.status_code == 429


def test_500_is_retried_until_success() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return httpx.Response(500, text="Internal Server Error")
        return httpx.Response(200, json=[])

    with respx.mock as mock:
        mock.get(f"{BASE}/accounts").mock(side_effect=handler)
        client = TradeZeroClient(**CREDS)
        result = client.accounts.list_accounts()

    assert result == []
    assert call_count == 3


def test_500_exhausts_retries_raises_server_error() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )
        client = TradeZeroClient(**CREDS)
        with pytest.raises(ServerError) as exc_info:
            client.accounts.list_accounts()
    assert exc_info.value.status_code == 500


def test_404_is_not_retried() -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(404, json={"message": "Account not found"})

    with respx.mock as mock:
        mock.get(f"{BASE}/account/MISSING").mock(side_effect=handler)
        client = TradeZeroClient(**CREDS)
        with pytest.raises(NotFoundError):
            client.accounts.get_account_details("MISSING")

    assert call_count == 1


def test_401_is_not_retried() -> None:
    from tradezero.exceptions import AuthenticationError

    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(401, json={"message": "Unauthorized"})

    with respx.mock as mock:
        mock.get(f"{BASE}/accounts").mock(side_effect=handler)
        client = TradeZeroClient(**CREDS)
        with pytest.raises(AuthenticationError):
            client.accounts.list_accounts()

    assert call_count == 1
