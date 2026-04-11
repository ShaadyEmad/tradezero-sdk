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


def test_create_order_returns_order_response() -> None:
    with respx.mock as mock:
        mock.post(f"{BASE}/accounts/ACC1/order").mock(
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


def test_create_order_serializes_correct_enum_values() -> None:
    with respx.mock as mock:
        route = mock.post(f"{BASE}/accounts/ACC1/order")
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
    assert "quantity" not in sent_body


def test_create_order_custom_security_type() -> None:
    with respx.mock as mock:
        route = mock.post(f"{BASE}/accounts/ACC1/order")
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


def test_create_order_with_enum_members() -> None:
    from tradezero.enums import OrderSide, OrderType, TimeInForce

    with respx.mock as mock:
        mock.post(f"{BASE}/accounts/ACC1/order").mock(
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


def test_list_orders_returns_order_list() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/orders").mock(
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


def test_list_historical_orders_uses_path_param_url() -> None:
    with respx.mock as mock:
        route = mock.get(f"{BASE}/accounts/ACC1/orders/start-date/2026-01-01")
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
        assert "start-date" in str(route.calls[0].request.url)
        assert "2026-01-01" in str(route.calls[0].request.url)

    trade = trades[0]
    assert trade.trade_id == 12345
    assert trade.symbol == "AAPL"
    assert trade.qty == 100
    assert trade.canceled is False
    assert trade.currency == "USD"


def test_list_historical_orders_empty_response() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/orders/start-date/2026-01-01").mock(
            return_value=httpx.Response(200, json=[])
        )
        client = TradeZeroClient(**CREDS)
        trades = client.trading.list_historical_orders("ACC1", "2026-01-01")
    assert trades == []


def test_cancel_order_sends_delete_and_succeeds() -> None:
    with respx.mock as mock:
        mock.delete(f"{BASE}/accounts/ACC1/orders/ORD-001").mock(
            return_value=httpx.Response(204)
        )
        client = TradeZeroClient(**CREDS)
        client.trading.cancel_order("ACC1", "ORD-001")


def test_cancel_all_orders_sends_account_in_form_body() -> None:
    with respx.mock as mock:
        route = mock.delete(f"{BASE}/accounts/orders")
        route.mock(return_value=httpx.Response(200, json={"message": "All orders canceled"}))

        client = TradeZeroClient(**CREDS)
        result = client.trading.cancel_all_orders("ACC1")

        request = route.calls[0].request
    assert result == {"message": "All orders canceled"}
    assert b"account=ACC1" in request.content


def test_cancel_all_orders_with_symbol_sends_query_param() -> None:
    with respx.mock as mock:
        route = mock.delete(f"{BASE}/accounts/orders")
        route.mock(return_value=httpx.Response(200, json={"message": "Done"}))

        client = TradeZeroClient(**CREDS)
        client.trading.cancel_all_orders("ACC1", symbol="AAPL")

        assert "symbol=AAPL" in str(route.calls[0].request.url)


def test_is_easy_to_borrow_true() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/is-easy-to-borrow/symbol/AAPL").mock(
            return_value=httpx.Response(200, json={"isEasyToBorrow": True})
        )
        client = TradeZeroClient(**CREDS)
        assert client.trading.is_easy_to_borrow("ACC1", "AAPL") is True


def test_is_easy_to_borrow_false() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/is-easy-to-borrow/symbol/GME").mock(
            return_value=httpx.Response(200, json={"isEasyToBorrow": False})
        )
        client = TradeZeroClient(**CREDS)
        assert client.trading.is_easy_to_borrow("ACC1", "GME") is False


def test_get_routes_returns_list() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/routes").mock(
            return_value=httpx.Response(
                200, json={"routes": [{"name": "SMART"}, {"name": "NSDQ"}]}
            )
        )
        client = TradeZeroClient(**CREDS)
        routes = client.trading.get_routes("ACC1")
    assert routes == [{"name": "SMART"}, {"name": "NSDQ"}]


def test_get_routes_empty_response() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/routes").mock(
            return_value=httpx.Response(200, json={})
        )
        client = TradeZeroClient(**CREDS)
        assert client.trading.get_routes("ACC1") == []
