"""Unit tests for the AccountsModule."""

from __future__ import annotations

import httpx
import respx

from tradezero import TradeZeroClient

BASE = "https://webapi.tradezero.com/v1/api"
CREDS = {"api_key": "test-key", "api_secret": "test-secret"}

# Full account payload matching the real API response structure
ACCOUNT_PAYLOAD = {
    "account": "ACC1",
    "accountStatus": "Active",
    "availableCash": 25000.0,
    "buyingPower": 50000.0,
    "equity": 75000.0,
    "leverage": 4.0,
    "overnightBp": 25000.0,
    "realized": 1500.0,
    "sharesTraded": 500,
    "sodEquity": 74000.0,
    "totalCommissions": 50.0,
    "totalLocateCosts": 10.0,
    "usedLeverage": 1.5,
    "optContractsTraded": 0,
    "optLevel": 1,
    "optionCashTotalBalance": 0.0,
    "optionTradingLevel": 1,
}

PNL_PAYLOAD = {
    "accountValue": 75000.0,
    "allowedLeverage": 4.0,
    "availableCash": 25000.0,
    "dayPnl": 1200.0,
    "dayRealized": 800.0,
    "dayUnrealized": 400.0,
    "equityRatio": 0.75,
    "exposure": 50000.0,
    "optionCashUsed": 0.0,
    "pnl": [],
    "sharesTraded": 500,
    "totalUnrealized": 400.0,
    "usedLeverage": 1.5,
}


# ── list_accounts ─────────────────────────────────────────────────────────────


@respx.mock
def test_list_accounts_returns_account_objects() -> None:
    """list_accounts parses all API fields into Account objects."""
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(200, json=[ACCOUNT_PAYLOAD])
    )
    client = TradeZeroClient(**CREDS)
    accounts = client.accounts.list_accounts()

    assert len(accounts) == 1
    acct = accounts[0]
    assert acct.account == "ACC1"
    assert acct.account_status == "Active"
    assert acct.buying_power == 50000.0
    assert acct.equity == 75000.0
    assert acct.realized == 1500.0
    assert acct.used_leverage == 1.5


@respx.mock
def test_list_accounts_wrapped_in_dict() -> None:
    """list_accounts handles an API response wrapped in {'accounts': [...]}."""
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(200, json={"accounts": [ACCOUNT_PAYLOAD]})
    )
    client = TradeZeroClient(**CREDS)
    accounts = client.accounts.list_accounts()
    assert len(accounts) == 1
    assert accounts[0].account == "ACC1"


@respx.mock
def test_list_accounts_empty_response() -> None:
    """list_accounts returns an empty list when the API returns []."""
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(200, json=[])
    )
    client = TradeZeroClient(**CREDS)
    assert client.accounts.list_accounts() == []


@respx.mock
def test_list_accounts_extra_fields_ignored() -> None:
    """Account model ignores unknown extra fields from the API."""
    payload = dict(ACCOUNT_PAYLOAD, unknownFutureField="should-not-crash")
    respx.get(f"{BASE}/accounts").mock(
        return_value=httpx.Response(200, json=[payload])
    )
    client = TradeZeroClient(**CREDS)
    accounts = client.accounts.list_accounts()
    assert accounts[0].account == "ACC1"


# ── get_account_details ───────────────────────────────────────────────────────


@respx.mock
def test_get_account_details_returns_account() -> None:
    """get_account_details returns an Account (not AccountDetails) with all fields."""
    respx.get(f"{BASE}/account/ACC1").mock(
        return_value=httpx.Response(200, json=ACCOUNT_PAYLOAD)
    )
    client = TradeZeroClient(**CREDS)
    acct = client.accounts.get_account_details("ACC1")

    from tradezero.models.accounts import Account

    assert isinstance(acct, Account)
    assert acct.account == "ACC1"
    assert acct.buying_power == 50000.0
    assert acct.used_leverage == 1.5
    assert acct.total_commissions == 50.0


# ── get_account_pnl ───────────────────────────────────────────────────────────


@respx.mock
def test_get_account_pnl_maps_all_fields() -> None:
    """get_account_pnl maps all real API fields to the correct attributes."""
    respx.get(f"{BASE}/accounts/ACC1/pnl").mock(
        return_value=httpx.Response(200, json=PNL_PAYLOAD)
    )
    client = TradeZeroClient(**CREDS)
    pnl = client.accounts.get_account_pnl("ACC1")

    assert pnl.account_value == 75000.0
    assert pnl.day_pnl == 1200.0
    assert pnl.day_realized == 800.0
    assert pnl.day_unrealized == 400.0
    assert pnl.total_unrealized == 400.0
    assert pnl.used_leverage == 1.5
    assert pnl.equity_ratio == 0.75
    assert pnl.pnl == []


@respx.mock
def test_get_account_pnl_extra_fields_ignored() -> None:
    """AccountPnL must not crash on extra fields returned by the API."""
    payload = dict(PNL_PAYLOAD, unknownFutureField="should-not-crash")
    respx.get(f"{BASE}/accounts/ACC1/pnl").mock(
        return_value=httpx.Response(200, json=payload)
    )
    client = TradeZeroClient(**CREDS)
    pnl = client.accounts.get_account_pnl("ACC1")
    assert pnl.account_value == 75000.0
