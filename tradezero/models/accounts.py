"""Pydantic models for the Accounts module."""

from __future__ import annotations

from pydantic import BaseModel, Field, AliasChoices


class Account(BaseModel):
    """Full account record returned by both ``GET /accounts`` and ``GET /account/:id``.

    Both endpoints return the same field structure per the TradeZero API docs.
    The ``get_account_details()`` method returns this model directly.

    Attributes:
        account: Unique account identifier (API field: ``account``).
        account_status: Current status of the account (e.g., ``"Active"``, ``"Suspended"``).
        available_cash: Cash available for trading and withdrawals.
        buying_power: Total buying power including leverage.
        equity: Total account equity (cash + market value of positions).
        leverage: Maximum leverage ratio allowed for the account.
        overnight_bp: Buying power available for overnight positions.
        realized: Realized profit/loss from closed positions.
        shares_traded: Total number of shares traded.
        sod_equity: Start-of-day equity balance.
        total_commissions: Total commissions paid.
        total_locate_costs: Total costs incurred for stock locates.
        used_leverage: Current leverage ratio being used.
        opt_contracts_traded: Number of option contracts traded.
        opt_level: Options trading level/tier.
        option_cash_total_balance: Total cash balance allocated for options.
        option_trading_level: Options trading authorization level.
    """

    account: str = Field(validation_alias=AliasChoices("account", "accountId"))
    account_status: str | None = Field(default=None, alias="accountStatus")
    available_cash: float = Field(default=0.0, alias="availableCash")
    buying_power: float = Field(default=0.0, alias="buyingPower")
    equity: float = Field(default=0.0)
    leverage: float = Field(default=0.0)
    overnight_bp: float = Field(default=0.0, alias="overnightBp")
    realized: float = Field(default=0.0)
    shares_traded: float = Field(default=0.0, alias="sharesTraded")
    sod_equity: float = Field(default=0.0, alias="sodEquity")
    total_commissions: float = Field(default=0.0, alias="totalCommissions")
    total_locate_costs: float = Field(default=0.0, alias="totalLocateCosts")
    used_leverage: float = Field(default=0.0, alias="usedLeverage")
    opt_contracts_traded: float = Field(default=0.0, alias="optContractsTraded")
    opt_level: float = Field(default=0.0, alias="optLevel")
    option_cash_total_balance: float = Field(default=0.0, alias="optionCashTotalBalance")
    option_trading_level: float = Field(default=0.0, alias="optionTradingLevel")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class AccountPnL(BaseModel):
    """Profit & loss, balance, and exposure metrics for an account.

    Returned by ``GET /accounts/:accountId/pnl``.

    Attributes:
        account_value: Total account value including cash and positions.
        allowed_leverage: Maximum leverage ratio permitted.
        available_cash: Cash available for trading.
        day_pnl: Total P&L for the current trading day (realized + unrealized).
        day_realized: Realized P&L for the current trading day.
        day_unrealized: Unrealized P&L for the current trading day.
        equity_ratio: Equity to total account value ratio.
        exposure: Total market exposure across all positions.
        option_cash_used: Cash currently allocated to options positions.
        pnl: Array of detailed P&L objects (may be empty).
        shares_traded: Total number of shares traded today.
        total_unrealized: Total unrealized P&L across all positions.
        used_leverage: Current leverage ratio being utilized.
    """

    account_value: float = Field(alias="accountValue")
    allowed_leverage: float = Field(alias="allowedLeverage")
    available_cash: float = Field(alias="availableCash")
    day_pnl: float = Field(alias="dayPnl")
    day_realized: float = Field(alias="dayRealized")
    day_unrealized: float = Field(alias="dayUnrealized")
    equity_ratio: float = Field(alias="equityRatio")
    exposure: float = Field(default=0.0)
    option_cash_used: float = Field(default=0.0, alias="optionCashUsed")
    pnl: list[dict] = Field(default_factory=list)
    shares_traded: float = Field(alias="sharesTraded")
    total_unrealized: float = Field(alias="totalUnrealized")
    used_leverage: float = Field(alias="usedLeverage")

    model_config = {"populate_by_name": True, "extra": "ignore"}
