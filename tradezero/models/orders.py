"""Pydantic models for the Trading / Orders module."""

from __future__ import annotations

from pydantic import AliasChoices, BaseModel, Field

from tradezero.enums import OrderSide, OrderType, SecurityType, TimeInForce


class CreateOrderRequest(BaseModel):
    """Payload for creating a new trade order.

    Attributes:
        symbol: Ticker symbol (e.g., ``"AAPL"``).
        order_quantity: Number of shares (wire name: ``orderQuantity``).
        side: ``"Buy"`` or ``"Sell"``.
        order_type: Execution style (e.g., ``"Limit"``, ``"Market"``).
        time_in_force: Duration instruction (e.g., ``"Day"``, ``"GoodTillCancel"``).
        security_type: ``"Stock"`` or ``"Option"`` (defaults to ``"Stock"``).
        limit_price: Required for ``Limit`` and ``StopLimit`` orders.
        stop_price: Required for ``Stop`` and ``StopLimit`` orders.
        client_order_id: Optional caller-supplied order identifier (max 375 chars).
        route: Optional routing destination (e.g., ``"SMART"``).
    """

    symbol: str
    order_quantity: int = Field(gt=0, alias="orderQuantity")
    side: OrderSide
    order_type: OrderType = Field(alias="orderType")
    time_in_force: TimeInForce = Field(alias="timeInForce")
    security_type: SecurityType = Field(default=SecurityType.STOCK, alias="securityType")
    limit_price: float | None = Field(default=None, alias="limitPrice")
    stop_price: float | None = Field(default=None, alias="stopPrice")
    client_order_id: str | None = Field(default=None, alias="clientOrderId")
    route: str | None = None

    model_config = {"populate_by_name": True}


class OrderResponse(BaseModel):
    """Response returned after placing a new order.

    Attributes:
        account_id: The account the order was sent from.
        order_status: Current status (e.g., ``"Pending"``, ``"Filled"``, ``"Rejected"``).
        executed: Quantity of shares already executed.
        leaves_quantity: Remaining quantity to be filled.
        price_avg: Average execution price.
        last_updated: Timestamp of the last status update.
        text: Informational text or error message from the exchange.
        margin_requirement: Margin required to hold this order.
    """

    account_id: str = Field(alias="accountId")
    order_status: str = Field(alias="orderStatus")
    executed: float = Field(default=0.0)
    leaves_quantity: float = Field(default=0.0, alias="leavesQuantity")
    price_avg: float = Field(default=0.0, alias="priceAvg")
    last_updated: str | None = Field(default=None, alias="lastUpdated")
    text: str | None = None
    margin_requirement: float = Field(default=0.0, alias="marginRequirement")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class Order(BaseModel):
    """Full order record returned when listing current-day orders.

    Attributes:
        client_order_id: Unique order identifier.
        symbol: Ticker symbol.
        side: Buy or sell.
        quantity: Requested quantity.
        order_type: Execution style.
        time_in_force: Duration instruction.
        order_status: Current lifecycle status.
        filled_quantity: Executed quantity so far.
        average_price: Average fill price.
        limit_price: Limit price if applicable.
        stop_price: Stop price if applicable.
    """

    client_order_id: str = Field(alias="clientOrderId")
    symbol: str = Field(validation_alias=AliasChoices("symbol", "tradedSymbol"))
    side: str
    quantity: int = Field(validation_alias=AliasChoices("quantity", "orderQuantity"))
    order_type: str = Field(alias="orderType")
    time_in_force: str = Field(alias="timeInForce")
    order_status: str = Field(alias="orderStatus")
    filled_quantity: int = Field(default=0, alias="filledQuantity")
    average_price: float = Field(default=0.0, alias="averagePrice")
    limit_price: float | None = Field(default=None, alias="limitPrice")
    stop_price: float | None = Field(default=None, alias="stopPrice")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class TradeRecord(BaseModel):
    """Historical trade record returned by the orders/start-date endpoint.

    This model represents executed trades, not live orders. The fields differ
    significantly from :class:`Order` (which represents current-day order state).

    Attributes:
        account_id: Account identifier.
        trade_id: Unique trade identifier.
        symbol: Ticker symbol of the traded security.
        qty: Quantity of shares traded.
        price: Price per share.
        side: Trade direction (``"Buy"`` / ``"Sell"``), may be absent.
        trade_date: Date when the trade was executed (ISO 8601).
        settle_date: Date when the trade settles (ISO 8601).
        entry_date: Date when the trade was entered into the system (ISO 8601).
        exec_time: Time the trade was executed, if available.
        gross_proceeds: Gross proceeds from the trade.
        net_proceeds: Net proceeds after fees and commissions.
        commission: Commission charged for the trade.
        total_fees: Total fees associated with the trade, if available.
        canceled: Whether the trade was cancelled.
        currency: Currency used for the trade.
        security_type: Type of security traded, if available.
        notes: Additional notes about the trade, if available.
    """

    account_id: str = Field(alias="accountId")
    trade_id: int = Field(alias="tradeId")
    symbol: str
    qty: int
    price: float
    side: str | None = None
    trade_date: str = Field(alias="tradeDate")
    settle_date: str = Field(alias="settleDate")
    entry_date: str = Field(alias="entryDate")
    exec_time: str | None = Field(default=None, alias="execTime")
    gross_proceeds: float = Field(alias="grossProceeds")
    net_proceeds: float = Field(alias="netProceeds")
    commission: float
    total_fees: float | None = Field(default=None, alias="totalFees")
    canceled: bool
    currency: str
    security_type: str | None = Field(default=None, alias="securityType")
    notes: str | None = None

    model_config = {"populate_by_name": True, "extra": "ignore"}
