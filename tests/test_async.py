"""Unit tests for AsyncTradeZeroClient."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from tradezero import AsyncTradeZeroClient

BASE = "https://webapi.tradezero.com/v1/api"
CREDS = {"api_key": "test-key", "api_secret": "test-secret"}

ACCOUNT_PAYLOAD = {
    "account": "ACC1",
    "accountStatus": "Active",
    "availableCash": 10000.0,
    "buyingPower": 40000.0,
    "equity": 50000.0,
    "leverage": 4.0,
    "overnightBp": 10000.0,
    "realized": 0.0,
    "sharesTraded": 0,
    "sodEquity": 50000.0,
    "totalCommissions": 0.0,
    "totalLocateCosts": 0.0,
    "usedLeverage": 0.0,
    "optContractsTraded": 0,
    "optLevel": 0,
    "optionCashTotalBalance": 0.0,
    "optionTradingLevel": 0,
}

ORDER_RESPONSE = {
    "accountId": "ACC1",
    "orderStatus": "Pending",
    "executed": 0.0,
    "leavesQuantity": 50.0,
    "priceAvg": 0.0,
    "lastUpdated": None,
    "text": None,
    "marginRequirement": 0.0,
}


@pytest.mark.asyncio
async def test_async_list_accounts() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts").mock(
            return_value=httpx.Response(200, json=[ACCOUNT_PAYLOAD])
        )
        async with AsyncTradeZeroClient(**CREDS) as client:
            accounts = await client.accounts.list_accounts()

    assert len(accounts) == 1
    assert accounts[0].account == "ACC1"
    assert accounts[0].buying_power == 40000.0


@pytest.mark.asyncio
async def test_async_get_account_details() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/account/ACC1").mock(
            return_value=httpx.Response(200, json=ACCOUNT_PAYLOAD)
        )
        async with AsyncTradeZeroClient(**CREDS) as client:
            acct = await client.accounts.get_account_details("ACC1")

    assert acct.account == "ACC1"
    assert acct.equity == 50000.0


@pytest.mark.asyncio
async def test_async_get_positions_with_unrealized_pnl() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/positions").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "symbol": "AAPL",
                        "shares": 100,
                        "side": "Long",
                        "priceAvg": 180.0,
                        "priceClose": 190.0,
                        "dayOvernight": "Day",
                    }
                ],
            )
        )
        async with AsyncTradeZeroClient(**CREDS) as client:
            positions = await client.positions.get_positions("ACC1")

    assert len(positions) == 1
    assert positions[0].unrealized_pnl == pytest.approx(1000.0)


@pytest.mark.asyncio
async def test_async_create_order() -> None:
    with respx.mock as mock:
        mock.post(f"{BASE}/accounts/ACC1/order").mock(
            return_value=httpx.Response(200, json=ORDER_RESPONSE)
        )
        async with AsyncTradeZeroClient(**CREDS) as client:
            resp = await client.trading.create_order(
                account_id="ACC1",
                symbol="AAPL",
                quantity=50,
                side="Buy",
                order_type="Market",
                time_in_force="Day",
            )

    assert resp.account_id == "ACC1"
    assert resp.order_status == "Pending"
    assert resp.leaves_quantity == 50.0


@pytest.mark.asyncio
async def test_async_create_order_serializes_correct_body() -> None:
    with respx.mock as mock:
        route = mock.post(f"{BASE}/accounts/ACC1/order")
        route.mock(return_value=httpx.Response(200, json=ORDER_RESPONSE))

        async with AsyncTradeZeroClient(**CREDS) as client:
            await client.trading.create_order(
                account_id="ACC1",
                symbol="TSLA",
                quantity=25,
                side="Sell",
                order_type="Limit",
                time_in_force="GoodTillCancel",
                limit_price=300.0,
            )

        body = json.loads(route.calls[0].request.content)
    assert body["side"] == "Sell"
    assert body["orderType"] == "Limit"
    assert body["orderQuantity"] == 25
    assert body["securityType"] == "Stock"


@pytest.mark.asyncio
async def test_async_cancel_order() -> None:
    with respx.mock as mock:
        mock.delete(f"{BASE}/accounts/ACC1/orders/ORD-001").mock(
            return_value=httpx.Response(204)
        )
        async with AsyncTradeZeroClient(**CREDS) as client:
            await client.trading.cancel_order("ACC1", "ORD-001")


@pytest.mark.asyncio
async def test_async_is_easy_to_borrow() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/is-easy-to-borrow/symbol/AAPL").mock(
            return_value=httpx.Response(200, json={"isEasyToBorrow": True})
        )
        async with AsyncTradeZeroClient(**CREDS) as client:
            result = await client.trading.is_easy_to_borrow("ACC1", "AAPL")

    assert result is True


@pytest.mark.asyncio
async def test_async_cancel_all_orders() -> None:
    with respx.mock as mock:
        route = mock.delete(f"{BASE}/accounts/orders")
        route.mock(return_value=httpx.Response(200, json={"message": "All canceled"}))

        async with AsyncTradeZeroClient(**CREDS) as client:
            result = await client.trading.cancel_all_orders("ACC1")

        assert b"account=ACC1" in route.calls[0].request.content
    assert result == {"message": "All canceled"}


@pytest.mark.asyncio
async def test_async_request_quote() -> None:
    with respx.mock as mock:
        route = mock.post(f"{BASE}/accounts/locates/quote")
        route.mock(return_value=httpx.Response(200, json={"locateQuoteSent": "ok"}))

        async with AsyncTradeZeroClient(**CREDS) as client:
            result = await client.locates.request_quote("ACC1", "GME", 500, "REQ-ASYNC-001")

        body = json.loads(route.calls[0].request.content)
    assert result == {"locateQuoteSent": "ok"}
    assert body["quoteReqID"] == "REQ-ASYNC-001"


SINGLE_ORDER_PAYLOAD = {
    "clientOrderId": "ORD-ASYNC-01",
    "symbol": "NVDA",
    "side": "Buy",
    "quantity": 20,
    "orderType": "Market",
    "timeInForce": "Day",
    "orderStatus": "new",
    "filledQuantity": 0,
    "averagePrice": 0.0,
}

TRADE_RECORD_PAYLOAD = {
    "accountId": "ACC1",
    "tradeId": 7777,
    "symbol": "NVDA",
    "qty": 20,
    "price": 800.0,
    "side": "Buy",
    "tradeDate": "2026-01-01T10:00:00Z",
    "settleDate": "2026-01-03T00:00:00Z",
    "entryDate": "2026-01-01T09:59:00Z",
    "grossProceeds": 16000.0,
    "netProceeds": 15990.0,
    "commission": 5.0,
    "canceled": False,
    "currency": "USD",
}


@pytest.mark.asyncio
async def test_async_get_order_returns_order() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/order/ORD-ASYNC-01").mock(
            return_value=httpx.Response(200, json=SINGLE_ORDER_PAYLOAD)
        )
        async with AsyncTradeZeroClient(**CREDS) as client:
            order = await client.trading.get_order("ACC1", "ORD-ASYNC-01")

    assert order.client_order_id == "ORD-ASYNC-01"
    assert order.symbol == "NVDA"
    assert order.quantity == 20


@pytest.mark.asyncio
async def test_async_list_historical_orders_paginated() -> None:
    with respx.mock as mock:
        mock.get(
            f"{BASE}/accounts/ACC1/orders-with-pagination/start-date/2026-01-01"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "trades": [TRADE_RECORD_PAYLOAD],
                    "page": 1,
                    "pageSize": 100,
                    "totalCount": 1,
                },
            )
        )
        async with AsyncTradeZeroClient(**CREDS) as client:
            result = await client.trading.list_historical_orders_paginated(
                "ACC1", "2026-01-01"
            )

    assert len(result.trades) == 1
    assert result.trades[0].trade_id == 7777
    assert result.page == 1
    assert result.total_count == 1


def test_async_client_missing_api_key_raises_value_error() -> None:
    with pytest.raises(ValueError, match="api_key"):
        AsyncTradeZeroClient(api_key=None, api_secret="secret")  # type: ignore[arg-type]


def test_async_client_missing_api_secret_raises_value_error() -> None:
    with pytest.raises(ValueError, match="api_secret"):
        AsyncTradeZeroClient(api_key="key", api_secret=None)  # type: ignore[arg-type]
