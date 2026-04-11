"""Domain modules that wrap TradeZero API resources.

These are attached as attributes on the client classes; not meant for
direct instantiation.
"""

from tradezero.modules.accounts import AccountsModule, AsyncAccountsModule
from tradezero.modules.locates import AsyncLocatesModule, LocatesModule
from tradezero.modules.positions import AsyncPositionsModule, PositionsModule
from tradezero.modules.trading import AsyncTradingModule, TradingModule

__all__ = [
    "AccountsModule",
    "AsyncAccountsModule",
    "TradingModule",
    "AsyncTradingModule",
    "PositionsModule",
    "AsyncPositionsModule",
    "LocatesModule",
    "AsyncLocatesModule",
]
