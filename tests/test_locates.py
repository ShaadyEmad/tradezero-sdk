"""Unit tests for the LocatesModule."""

from __future__ import annotations

import json

import httpx
import respx

from tradezero import TradeZeroClient
from tradezero.enums import LocateStatus

BASE = "https://webapi.tradezero.com/v1/api"
CREDS = {"api_key": "test-key", "api_secret": "test-secret"}


def test_request_quote_posts_correct_body() -> None:
    with respx.mock as mock:
        route = mock.post(f"{BASE}/accounts/locates/quote")
        route.mock(return_value=httpx.Response(200, json={"locateQuoteSent": "ok"}))

        client = TradeZeroClient(**CREDS)
        result = client.locates.request_quote("ACC1", "GME", 1000, "REQ-001")

        body = json.loads(route.calls[0].request.content)
    assert result == {"locateQuoteSent": "ok"}
    assert body["account"] == "ACC1"
    assert body["symbol"] == "GME"
    assert body["quantity"] == 1000
    assert body["quoteReqID"] == "REQ-001"


def test_get_inventory_returns_items() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/locates/inventory").mock(
            return_value=httpx.Response(
                200,
                json={
                    "locateInventory": [
                        {"available": 5000, "sold": 100, "unavailable": 0, "locateType": 1}
                    ]
                },
            )
        )
        client = TradeZeroClient(**CREDS)
        items = client.locates.get_inventory("ACC1")

    assert len(items) == 1
    assert items[0].available == 5000
    assert items[0].sold == 100
    assert items[0].locate_type == 1


def test_get_inventory_empty() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/locates/inventory").mock(
            return_value=httpx.Response(200, json={"locateInventory": []})
        )
        client = TradeZeroClient(**CREDS)
        assert client.locates.get_inventory("ACC1") == []


def test_get_history_returns_items_with_correct_status() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/locates/history").mock(
            return_value=httpx.Response(
                200,
                json={
                    "locateHistory": [
                        {
                            "quoteReqID": "REQ-001",
                            "symbol": "GME",
                            "quantity": 500,
                            "locateStatus": 65,
                            "rate": 0.05,
                        }
                    ]
                },
            )
        )
        client = TradeZeroClient(**CREDS)
        history = client.locates.get_history("ACC1")

    assert len(history) == 1
    item = history[0]
    assert item.quote_req_id == "REQ-001"
    assert item.symbol == "GME"
    assert item.quantity == 500
    assert item.locate_status == LocateStatus.OFFERED
    assert item.rate == 0.05


def test_get_history_quoting_status() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/locates/history").mock(
            return_value=httpx.Response(
                200,
                json={
                    "locateHistory": [
                        {
                            "quoteReqID": "REQ-002",
                            "symbol": "TSLA",
                            "locateStatus": 81,
                            "rate": 0.0,
                        }
                    ]
                },
            )
        )
        client = TradeZeroClient(**CREDS)
        history = client.locates.get_history("ACC1")
    assert history[0].locate_status == LocateStatus.QUOTING


def test_accept_quote_posts_correct_body() -> None:
    with respx.mock as mock:
        route = mock.post(f"{BASE}/accounts/locates/accept")
        route.mock(return_value=httpx.Response(200, json={"locateAcceptSent": "ok"}))

        client = TradeZeroClient(**CREDS)
        result = client.locates.accept_quote("ACC1", "REQ-001")

        body = json.loads(route.calls[0].request.content)
    assert result == {"locateAcceptSent": "ok"}
    assert body["accountId"] == "ACC1"
    assert body["quoteReqID"] == "REQ-001"


def test_sell_locate_posts_correct_body() -> None:
    with respx.mock as mock:
        route = mock.post(f"{BASE}/accounts/locates/sell")
        route.mock(return_value=httpx.Response(200, json={"locateSellbackSent": "ok"}))

        client = TradeZeroClient(**CREDS)
        result = client.locates.sell_locate("ACC1", "GME", "REQ-002", 200, "Locate")

        body = json.loads(route.calls[0].request.content)
    assert result == {"locateSellbackSent": "ok"}
    assert body["account"] == "ACC1"
    assert body["symbol"] == "GME"
    assert body["quoteReqID"] == "REQ-002"
    assert body["quantity"] == 200
    assert body["locateType"] == "Locate"


def test_cancel_locate_sends_delete() -> None:
    with respx.mock as mock:
        route = mock.delete(
            f"{BASE}/accounts/locates/cancel/accounts/ACC1/quoteReqID/REQ-001"
        )
        route.mock(return_value=httpx.Response(200, json={"locateCancelSent": "ok"}))

        client = TradeZeroClient(**CREDS)
        client.locates.cancel_locate("ACC1", "REQ-001")

    assert route.called
