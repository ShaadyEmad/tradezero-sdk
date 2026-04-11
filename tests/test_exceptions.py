"""Unit tests for exception mapping."""

import respx
import httpx
import pytest

from tradezero import TradeZeroClient, RateLimitError, AuthenticationError, NotFoundError

BASE = "https://webapi.tradezero.com/v1/api"
CREDS = {"api_key": "test-key", "api_secret": "test-secret"}


@respx.mock
def test_401_raises_authentication_error():
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )
    client = TradeZeroClient(**CREDS)
    with pytest.raises(AuthenticationError) as exc_info:
        client.accounts.list_accounts()
    assert exc_info.value.status_code == 401


@respx.mock
def test_429_raises_rate_limit_error():
    # All retries should also return 429; disable retries by patching max attempts
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(429, json={"message": "Too many requests"})
    )
    client = TradeZeroClient(**CREDS)
    with pytest.raises(RateLimitError):
        client.accounts.list_accounts()


@respx.mock
def test_404_raises_not_found():
    respx.get(f"{BASE}/account/UNKNOWN").mock(
        return_value=httpx.Response(404, json={"message": "Account not found"})
    )
    client = TradeZeroClient(**CREDS)
    with pytest.raises(NotFoundError):
        client.accounts.get_account_details("UNKNOWN")
