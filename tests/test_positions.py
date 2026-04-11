"""Unit tests for the PositionsModule and Position model."""

from __future__ import annotations

import httpx
import pytest
import respx

from tradezero import TradeZeroClient

BASE = "https://webapi.tradezero.com/v1/api"
CREDS = {"api_key": "test-key", "api_secret": "test-secret"}


def test_get_positions_and_pnl() -> None:
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
                        "priceClose": 185.0,
                        "dayOvernight": "Day",
                    },
                    {
                        "symbol": "TSLA",
                        "shares": 50,
                        "side": "Short",
                        "priceAvg": 250.0,
                        "priceClose": 245.0,
                        "dayOvernight": "Overnight",
                    },
                ],
            )
        )
        client = TradeZeroClient(**CREDS)
        positions = client.positions.get_positions("ACC1")

    assert len(positions) == 2
    aapl = positions[0]
    assert aapl.symbol == "AAPL"
    assert aapl.unrealized_pnl == pytest.approx(500.0)

    tsla = positions[1]
    assert tsla.unrealized_pnl == pytest.approx(250.0)


def test_get_positions_empty() -> None:
    with respx.mock as mock:
        mock.get(f"{BASE}/accounts/ACC1/positions").mock(
            return_value=httpx.Response(200, json=[])
        )
        client = TradeZeroClient(**CREDS)
        assert client.positions.get_positions("ACC1") == []


def test_position_long_unrealized_pnl() -> None:
    from tradezero.models.positions import Position

    pos = Position(symbol="AAPL", shares=200, side="Long", priceAvg=100.0, priceClose=110.0)
    assert pos.unrealized_pnl == pytest.approx(2000.0)


def test_position_short_unrealized_pnl() -> None:
    from tradezero.models.positions import Position

    pos = Position(symbol="GME", shares=100, side="Short", priceAvg=200.0, priceClose=150.0)
    assert pos.unrealized_pnl == pytest.approx(5000.0)


def test_position_short_loss() -> None:
    from tradezero.models.positions import Position

    pos = Position(symbol="GME", shares=100, side="Short", priceAvg=100.0, priceClose=120.0)
    assert pos.unrealized_pnl == pytest.approx(-2000.0)
