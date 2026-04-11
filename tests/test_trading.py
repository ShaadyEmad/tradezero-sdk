"""Unit tests for the TradingModule."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from tradezero import TradeZeroClient
from tradezero.exceptions import APIValidationError

BASE = "https://webapi.tradezero.com/v1/api"
CREDS = {"api_key": "test-key", "api_secret": "test-secret"}

ORDER_RESPONSE = {
    "accountId": "ACC1",
    "orderStatus": "Pending",
    "executed": 0.0,
    "leavesQuantity": 100.0,
    "priceAvg": 0.0,
    "lastUpdated": "2026-01-01T10:00:00Z",
    "text": "",
    "marginRequirement": 0.0,
}


# ── create_order ──────────────────────────────────────────────────────────────


@respx.mock
def test_create_order_returns_order_response() -> None:
    """create_order returns a parsed OrderResponse with correct field mapping."""
    respx.post(f"{BASE}/accounts/ACC1/order").mock(
        return_value=httpx.Response(200, json=ORDER_RESPONSE)
    )
    client = TradeZeroClient(**CREDS)
    resp = client.trading.create_order(
        account_id="ACC1",
        symbol="AAPL",
        quantity=100,
        side="Buy",
        order_type="Limit",
        time_in_force="Day",
        limit_price=185.0,
    )
    assert resp.account_id == "ACC1"
    assert resp.order_status == "Pending"
    assert resp.leaves_quantity == 100.0
    assert resp.executed == 0.0


@respx.mock
def test_create_order_serializes_correct_enum_values() -> None:
    """Request body sent to the API must use PascalCase enum values and orderQuantity."""
    route = respx.post(f"{BASE}/accounts/ACC1/order")
    route.mock(return_value=httpx.Response(200, json=ORDER_RESPONSE))

    client = TradeZeroClient(**CREDS)
    client.trading.create_order(
        account_id="ACC1",
        symbol="TSLA",
        quantity=10,
        side="Sell",
        order_type="Market",
        time_in_force="GoodTillCancel",
    )

    sent_body = json.loads(route.calls[0].request.content)
    assert sent_body["side"] == "Sell"
    assert sent_body["orderType"] == "Market"
    assert sent_body["timeInForce"] == "GoodTillCancel"
    assert sent_body["securityType"] == "Stock"
    assert sent_body["orderQuantity"] == 10
    # Old field name must NOT appear
    assert "quantity" not in sent_body


@respx.mock
def test_create_order_custom_security_type() -> None:
    """security_type=Option is serialized correctly."""
    route = respx.post(f"{BASE}/accounts/ACC1/order")
    route.mock(return_value=httpx.Response(200, json=ORDER_RESPONSE))

    client = TradeZeroClient(**CREDS)
    client.trading.create_order(
        account_id="ACC1",
        symbol="AAPL240119C00185000",
        quantity=5,
        side="Buy",
        order_type="Limit",
        time_in_force="Day",
        security_type="Option",
        limit_price=2.50,
    )

    sent_body = json.loads(route.calls[0].request.content)
    assert sent_body["securityType"] == "Option"


@respx.mock
def test_create_order_with_enum_members() -> None:
    """Passing enum members directly (not strings) also works."""
    from tradezero.enums import OrderSide, OrderType, TimeInForce

    respx.post(f"{BASE}/accounts/ACC1/order").mock(
        return_value=httpx.Response(200, json=ORDER_RESPONSE)
    )
    client = TradeZeroClient(**CREDS)
    resp = client.trading.create_order(
        account_id="ACC1",
        symbol="MSFT",
        quantity=20,
        side=OrderSide.BUY,
        order_type=OrderType.STOP_LIMIT,
        time_in_force=TimeInForce.IOC,
        limit_price=400.0,
        stop_price=395.0,
    )
    assert resp.order_status == "Pending"


def test_create_order_invalid_side_raises_api_validation_error() -> None:
    """An invalid side value raises APIValidationError without a network call."""
    client = TradeZeroClient(**CREDS)
    with pytest.raises(APIValidationError):
        client.trading.create_order(
            account_id="ACC1",
            symbol="AAPL",
            quantity=10,
            side="invalid_side",
            order_type="Limit",
            time_in_force="Day",
        )


# ── list_orders ───────────────────────────────────────────────────────────────


@respx.mock
def test_list_orders_returns_order_list() -> None:
    """list_orders parses a list of current-day Order records."""
    respx.get(f"{BASE}/accounts/ACC1/orders").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "clientOrderId": "ORD-001",
                    "symbol": "AAPL",
                    "side": "Buy",
                    "quantity": 100,
                    "orderType": "Limit",
                    "timeInForce": "Day",
                    "orderStatus": "new",
                    "filledQuantity": 0,
                    "averagePrice": 0.0,
                }
            ],
        )
    )
    client = TradeZeroClient(**CREDS)
    orders = client.trading.list_orders("ACC1")
    assert len(orders) == 1
    assert orders[0].client_order_id == "ORD-001"
    assert orders[0].symbol == "AAPL"


# ── list_historical_orders ────────────────────────────────────────────────────


@respx.mock
def test_list_historical_orders_uses_path_param_url() -> None:
    """list_historical_orders must call /orders/start-date/{date}, not a query param."""
    route = respx.get(f"{BASE}/accounts/ACC1/orders/start-date/2026-01-01")
    route.mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "accountId": "ACC1",
                    "tradeId": 12345,
                    "symbol": "AAPL",
                    "qty": 100,
                    "price": 185.0,
                    "side": "Buy",
                    "tradeDate": "2026-01-01T10:00:00Z",
                    "settleDate": "2026-01-03T00:00:00Z",
                    "entryDate": "2026-01-01T09:59:00Z",
                    "grossProceeds": 18500.0,
                    "netProceeds": 18475.0,
                    "commission": 5.0,
                    "canceled": False,
                    "currency": "USD",
                }
            ],
        )
    )
    client = TradeZeroClient(**CREDS)
    trades = client.trading.list_historical_orders("ACC1", "2026-01-01")

    assert len(trades) == 1
    trade = trades[0]
    assert trade.trade_id == 12345
    assert trade.symbol == "AAPL"
    assert trade.qty == 100
    assert trade.canceled is False
    assert trade.currency == "USD"
    # Verify the correct URL path was called
    assert "start-date" in str(route.calls[0].request.url)
    assert "2026-01-01" in str(route.calls[0].request.url)


@respx.mock
def test_list_historical_orders_empty_response() -> None:
    """list_historical_orders returns empty list when no trades found."""
    respx.get(f"{BASE}/accounts/ACC1/orders/start-date/2026-01-01").mock(
        return_value=httpx.Response(200, json=[])
    )
    client = TradeZeroClient(**CREDS)
    trades = client.trading.list_historical_orders("ACC1", "2026-01-01")
    assert trades == []


# ── cancel_order ──────────────────────────────────────────────────────────────


@respx.mock
def test_cancel_order_sends_delete_and_succeeds() -> None:
    """cancel_order sends DELETE and raises no exception on 204."""
    respx.delete(f"{BASE}/accounts/ACC1/orders/ORD-001").mock(
        return_value=httpx.Response(204)
    )
    client = TradeZeroClient(**CREDS)
    client.trading.cancel_order("ACC1", "ORD-001")  # should not raise


# ── cancel_all_orders ─────────────────────────────────────────────────────────


@respx.mock
def test_cancel_all_orders_sends_account_in_form_body() -> None:
    """cancel_all_orders sends account ID as form data in the request body."""
    route = respx.delete(f"{BASE}/accounts/orders")
    route.mock(return_value=httpx.Response(200, json={"message": "All orders canceled"}))

    client = TradeZeroClient(**CREDS)
    result = client.trading.cancel_all_orders("ACC1")

    assert result == {"message": "All orders canceled"}
    request = route.calls[0].request
    # Form body must contain the account field
    assert b"account=ACC1" in request.content


@respx.mock
def test_cancel_all_orders_with_symbol_sends_query_param() -> None:
    """cancel_all_orders passes optional symbol as a query parameter."""
    route = respx.delete(f"{BASE}/accounts/orders")
    route.mock(return_value=httpx.Response(200, json={"message": "Done"}))

    client = TradeZeroClient(**CREDS)
    client.trading.cancel_all_orders("ACC1", symbol="AAPL")

    assert "symbol=AAPL" in str(route.calls[0].request.url)


# ── is_easy_to_borrow ─────────────────────────────────────────────────────────


@respx.mock
def test_is_easy_to_borrow_true() -> None:
    """is_easy_to_borrow returns True when API returns isEasyToBorrow=true."""
    respx.get(f"{BASE}/accounts/ACC1/is-easy-to-borrow/symbol/AAPL").mock(
        return_value=httpx.Response(200, json={"isEasyToBorrow": True})
    )
    client = TradeZeroClient(**CREDS)
    assert client.trading.is_easy_to_borrow("ACC1", "AAPL") is True


@respx.mock
def test_is_easy_to_borrow_false() -> None:
    """is_easy_to_borrow returns False when API returns isEasyToBorrow=false."""
    respx.get(f"{BASE}/accounts/ACC1/is-easy-to-borrow/symbol/GME").mock(
        return_value=httpx.Response(200, json={"isEasyToBorrow": False})
    )
    client = TradeZeroClient(**CREDS)
    assert client.trading.is_easy_to_borrow("ACC1", "GME") is False


# ── get_routes ────────────────────────────────────────────────────────────────


@respx.mock
def test_get_routes_returns_list() -> None:
    """get_routes returns the routes array from the API response."""
    respx.get(f"{BASE}/accounts/ACC1/routes").mock(
        return_value=httpx.Response(
            200, json={"routes": [{"name": "SMART"}, {"name": "NSDQ"}]}
        )
    )
    client = TradeZeroClient(**CREDS)
    routes = client.trading.get_routes("ACC1")
    assert routes == [{"name": "SMART"}, {"name": "NSDQ"}]


@respx.mock
def test_get_routes_empty_response() -> None:
    """get_routes returns empty list when routes array is absent."""
    respx.get(f"{BASE}/accounts/ACC1/routes").mock(
        return_value=httpx.Response(200, json={})
    )
    client = TradeZeroClient(**CREDS)
    assert client.trading.get_routes("ACC1") == []
