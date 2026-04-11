"""Pydantic models for the Positions module."""

from __future__ import annotations

from pydantic import BaseModel, Field, computed_field


class Position(BaseModel):
    """An open trading position with unrealised P&L calculation.

    Attributes:
        symbol: Ticker symbol.
        shares: Number of shares held (positive).
        side: ``"Long"`` or ``"Short"``.
        price_avg: Average entry price.
        price_close: Most recent close / last price.
        day_overnight: Whether the position is intraday or overnight.
    """

    symbol: str
    shares: int
    side: str
    price_avg: float = Field(default=0.0, alias="priceAvg")
    price_close: float = Field(default=0.0, alias="priceClose")
    day_overnight: str = Field(default="", alias="dayOvernight")

    model_config = {"populate_by_name": True, "extra": "ignore"}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealised P&L based on position direction.

        For **Long** positions: ``(priceClose - priceAvg) * shares``
        For **Short** positions: ``(priceAvg - priceClose) * shares``

        Returns:
            Unrealised profit or loss in account currency.
        """
        if self.side.lower() == "long":
            return (self.price_close - self.price_avg) * self.shares
        # Short position: profit when price falls
        return (self.price_avg - self.price_close) * self.shares
