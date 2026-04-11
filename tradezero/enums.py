"""Enumerations used across the TradeZero API."""

from enum import Enum


# ── Order enums ───────────────────────────────────────────────────────────────


class OrderSide(str, Enum):
    """Direction of a trade order.

    Values match the TradeZero API wire format exactly.
    """

    BUY = "Buy"
    SELL = "Sell"


class OrderType(str, Enum):
    """Execution style of a trade order.

    Values match the TradeZero API wire format exactly.
    """

    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "Stop"
    STOP_LIMIT = "StopLimit"


class TimeInForce(str, Enum):
    """Time-in-force instructions for a trade order.

    Values match the TradeZero API wire format exactly.
    """

    DAY = "Day"
    GTC = "GoodTillCancel"
    IOC = "ImmediateOrCancel"
    FOK = "FillOrKill"
    AT_THE_OPENING = "AtTheOpening"
    GOOD_TILL_CROSSING = "GoodTillCrossing"
    DAY_PLUS = "Day_Plus"
    GTC_PLUS = "GTC_Plus"


class SecurityType(str, Enum):
    """Type of security for an order.

    Values match the TradeZero API wire format exactly.
    """

    STOCK = "Stock"
    OPTION = "Option"


# ── Locate enums ──────────────────────────────────────────────────────────────


class LocateStatus(int, Enum):
    """Integer status codes for locate requests (FIX-style)."""

    NEW = 48
    FILLED = 50
    CANCELED = 52
    PENDING = 54
    REJECTED = 56
    OFFERED = 65
    EXPIRED = 67
    QUOTING = 81


class LocateTypeStr(str, Enum):
    """Human-readable locate type strings."""

    UNKNOWN = "Unknown"
    LOCATE = "Locate"
    INTRADAY = "IntraDay"
    PRE_BORROW = "PreBorrow"
    SINGLE_USE = "SingleUse"
