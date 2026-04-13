# tradezero-sdk — Complete Documentation

**Version:** 1.0.0 | **Author:** Shady Emad | **License:** MIT

> This document is the complete reference for the tradezero-sdk package.
> For a quick overview see [README.md](README.md). For version history see [CHANGELOG.md](CHANGELOG.md).
> To contribute see [CONTRIBUTING.md](CONTRIBUTING.md). For security reporting see [SECURITY.md](SECURITY.md).

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation](#2-installation)
3. [Authentication & Configuration](#3-authentication--configuration)
4. [Client Lifecycle](#4-client-lifecycle)
5. [Accounts Module](#5-accounts-module)
6. [Positions Module](#6-positions-module)
7. [Trading Module](#7-trading-module)
8. [Locates Module](#8-locates-module)
9. [Data Models](#9-data-models)
10. [Enumerations](#10-enumerations)
11. [Exception Handling](#11-exception-handling)
12. [Retry Behaviour](#12-retry-behaviour)
13. [Async Usage](#13-async-usage)
14. [Environment Variables Reference](#14-environment-variables-reference)
15. [Package Structure](#15-package-structure)

---

## 1. Overview

tradezero-sdk is an unofficial Python client library for the TradeZero REST API. It handles:

- HTTP communication and authentication headers
- JSON request/response serialization with full type safety via Pydantic v2
- Automatic retry with exponential backoff for transient errors
- A structured exception hierarchy that maps HTTP status codes to named exceptions
- Both synchronous and asynchronous operation modes

All public classes and exceptions are importable directly from the top-level `tradezero` package.

```python
from tradezero import (
    TradeZeroClient,         # sync client
    AsyncTradeZeroClient,    # async client
    AuthenticationError,
    TradeZeroAPIError,
    # ... (see Section 11)
)
```

---

## 2. Installation

### From PyPI

```bash
pip install tradezero-sdk
```

### From Source

```bash
git clone https://github.com/shadyemad/tradezero-sdk.git
cd tradezero-sdk
pip install poetry
poetry install
```

**Requirements:** Python 3.11 or later.

**Runtime dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | ≥ 0.27 | HTTP client (sync + async) |
| `pydantic` | ^2.7 | Data validation and serialization |
| `tenacity` | ^8.3 | Retry logic with exponential backoff |

---

## 3. Authentication & Configuration

### API Credentials

You need a TradeZero API Key ID and API Secret Key. These are set as HTTP headers on every request:

```
TZ-API-KEY-ID:     <your api key>
TZ-API-SECRET-KEY: <your api secret>
```

### Passing Credentials

**Option A — Explicit constructor arguments (recommended for scripts):**

```python
from tradezero import TradeZeroClient

client = TradeZeroClient(api_key="YOUR_KEY", api_secret="YOUR_SECRET")
```

**Option B — Environment variables (recommended for production):**

```bash
export TZ_API_KEY="your-api-key"
export TZ_API_SECRET="your-api-secret"
```

```python
from tradezero import TradeZeroClient

client = TradeZeroClient()  # reads from env automatically
```

### Constructor Parameters

Both `TradeZeroClient` and `AsyncTradeZeroClient` accept the same keyword-only parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str \| None` | `None` → reads `TZ_API_KEY` env var | TradeZero API key ID |
| `api_secret` | `str \| None` | `None` → reads `TZ_API_SECRET` env var | TradeZero API secret key |
| `base_url` | `str \| None` | `None` → reads `TZ_BASE_URL` env var or uses default | API base URL |
| `timeout` | `float` | `30.0` | Per-request HTTP timeout in seconds |

Raises `ValueError` if `api_key` or `api_secret` cannot be resolved (neither provided nor in env).

### Base URL

The default base URL is:

```
https://webapi.tradezero.com/v1/api
```

Override it with the `TZ_BASE_URL` environment variable or the `base_url` constructor argument.

---

## 4. Client Lifecycle

### Synchronous Client — `TradeZeroClient`

Always use the client as a context manager to ensure HTTP connections are properly released:

```python
from tradezero import TradeZeroClient

# Recommended: context manager
with TradeZeroClient(api_key="...", api_secret="...") as client:
    accounts = client.accounts.list_accounts()
# Connection pool released here

# Manual lifecycle
client = TradeZeroClient(api_key="...", api_secret="...")
try:
    accounts = client.accounts.list_accounts()
finally:
    client.close()  # must call manually
```

**Methods:**

| Method | Description |
|--------|-------------|
| `close() -> None` | Release the underlying HTTP connection pool |
| `__enter__() -> TradeZeroClient` | Context manager entry |
| `__exit__(...) -> None` | Context manager exit (calls `close()`) |

**Module attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `client.accounts` | `AccountsModule` | Account and P&L endpoints |
| `client.positions` | `PositionsModule` | Open positions endpoint |
| `client.trading` | `TradingModule` | Orders, routes, borrow-check endpoints |
| `client.locates` | `LocatesModule` | Short-sell locate endpoints |

### Asynchronous Client — `AsyncTradeZeroClient`

```python
import asyncio
from tradezero import AsyncTradeZeroClient

async def main():
    async with AsyncTradeZeroClient(api_key="...", api_secret="...") as client:
        accounts = await client.accounts.list_accounts()

asyncio.run(main())

# Manual lifecycle
client = AsyncTradeZeroClient(api_key="...", api_secret="...")
try:
    accounts = await client.accounts.list_accounts()
finally:
    await client.aclose()
```

**Methods:**

| Method | Description |
|--------|-------------|
| `async aclose() -> None` | Release the underlying async HTTP connection pool |
| `async __aenter__() -> AsyncTradeZeroClient` | Async context manager entry |
| `async __aexit__(...) -> None` | Async context manager exit (calls `aclose()`) |

All module methods on `AsyncTradeZeroClient` are `async` and must be awaited.

---

## 5. Accounts Module

Accessible as `client.accounts`.

### `list_accounts() -> list[Account]`

Returns all accounts associated with the API credentials.

```python
accounts = client.accounts.list_accounts()

for acct in accounts:
    print(acct.account)         # e.g. "ABC123"
    print(acct.equity)          # total equity
    print(acct.buying_power)    # available buying power
    print(acct.available_cash)  # cash available
    print(acct.account_status)  # "Active", "Suspended", etc.
```

**Returns:** `list[Account]` — empty list if no accounts exist.

**Raises:** `AuthenticationError` if credentials are invalid.

---

### `get_account_details(account_id: str) -> Account`

Returns the full account record for a specific account ID. Returns the same `Account` model as `list_accounts()`.

```python
account_id = "ABC123"
details = client.accounts.get_account_details(account_id)

print(details.buying_power)
print(details.used_leverage)
print(details.total_commissions)
print(details.overnight_bp)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |

**Returns:** `Account`

**Raises:** `NotFoundError` if the account does not exist.

---

### `get_account_pnl(account_id: str) -> AccountPnL`

Returns daily P&L, balance, and exposure metrics for an account.

```python
pnl = client.accounts.get_account_pnl("ABC123")

print(f"Day P&L:    {pnl.day_pnl:+,.2f}")
print(f"Realized:   {pnl.day_realized:+,.2f}")
print(f"Unrealized: {pnl.day_unrealized:+,.2f}")
print(f"Cash:       {pnl.available_cash:,.2f}")
print(f"Leverage:   {pnl.used_leverage:.1f}x / {pnl.allowed_leverage:.1f}x max")
print(f"Exposure:   {pnl.exposure:,.2f}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |

**Returns:** `AccountPnL`

---

## 6. Positions Module

Accessible as `client.positions`.

### `get_positions(account_id: str) -> list[Position]`

Returns all currently open positions for an account, each with a computed `unrealized_pnl` field.

```python
positions = client.positions.get_positions("ABC123")

for pos in positions:
    print(f"Symbol:    {pos.symbol}")
    print(f"Side:      {pos.side}")          # "Long" or "Short"
    print(f"Shares:    {pos.shares}")
    print(f"Avg price: {pos.price_avg:.2f}")
    print(f"Last:      {pos.price_close:.2f}")
    print(f"Unreal PnL: {pos.unrealized_pnl:+,.2f}")
    print(f"Day/ONight: {pos.day_overnight}")
    print()
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |

**Returns:** `list[Position]` — empty list if no positions are open.

**`unrealized_pnl` calculation:**

```
Long:  (price_close - price_avg) × shares
Short: (price_avg - price_close) × shares
```

This is a computed property — it is not returned by the API, it is calculated locally by the SDK.

---

## 7. Trading Module

Accessible as `client.trading`.

### `create_order(...) -> OrderResponse`

Places a new trade order. Both string literals and enum members are accepted for `side`, `order_type`, `time_in_force`, and `security_type`.

```python
from tradezero.enums import OrderSide, OrderType, TimeInForce

resp = client.trading.create_order(
    account_id="ABC123",
    symbol="AAPL",
    quantity=100,
    side=OrderSide.BUY,        # or "Buy"
    order_type=OrderType.LIMIT, # or "Limit"
    time_in_force=TimeInForce.DAY,  # or "Day"
    limit_price=185.00,
    client_order_id="my-order-001",  # optional, your reference
)

print(resp.order_status)     # "Pending", "Filled", "Rejected", etc.
print(resp.account_id)
print(resp.executed)         # quantity already executed
print(resp.leaves_quantity)  # remaining quantity
print(resp.price_avg)        # average fill price
print(resp.text)             # message from exchange (if any)
print(resp.margin_requirement)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | `str` | Yes | Account to place the order on |
| `symbol` | `str` | Yes | Ticker symbol (e.g., `"AAPL"`) |
| `quantity` | `int` | Yes | Number of shares (must be > 0) |
| `side` | `OrderSide \| str` | Yes | `"Buy"` or `"Sell"` |
| `order_type` | `OrderType \| str` | Yes | `"Market"`, `"Limit"`, `"Stop"`, `"StopLimit"` |
| `time_in_force` | `TimeInForce \| str` | Yes | See [TimeInForce enum](#timeinforce) |
| `security_type` | `SecurityType \| str` | No | `"Stock"` (default) or `"Option"` |
| `limit_price` | `float \| None` | Conditional | Required for `Limit` and `StopLimit` orders |
| `stop_price` | `float \| None` | Conditional | Required for `Stop` and `StopLimit` orders |
| `client_order_id` | `str \| None` | No | Your own reference ID (max 375 chars) |
| `route` | `str \| None` | No | Routing destination (e.g., `"SMART"`) |

**Returns:** `OrderResponse`

**Raises:**
- `APIValidationError` — invalid parameters (e.g., quantity = 0)
- `InsufficientFundsError` — account has insufficient buying power
- `AuthenticationError` — invalid credentials

**Order type examples:**

```python
# Market order
client.trading.create_order(account_id, "TSLA", 10, "Buy", "Market", "Day")

# Limit buy
client.trading.create_order(account_id, "AAPL", 50, "Buy", "Limit", "Day",
    limit_price=180.00)

# Stop loss
client.trading.create_order(account_id, "AAPL", 50, "Sell", "Stop", "GoodTillCancel",
    stop_price=175.00)

# Stop-limit
client.trading.create_order(account_id, "AAPL", 50, "Sell", "StopLimit", "Day",
    stop_price=175.00, limit_price=174.50)

# Short sell (requires locate first if not easy-to-borrow)
client.trading.create_order(account_id, "GME", 100, "Sell", "Limit", "Day",
    limit_price=20.00)
```

---

### `get_order(account_id: str, order_id: str) -> Order`

Retrieves a single current-day order by its order ID.

```python
order = client.trading.get_order("ABC123", "ORD-001")
print(f"{order.client_order_id} | {order.symbol} | {order.side}")
print(f"  Status:   {order.order_status}")
print(f"  Qty:      {order.quantity} (filled: {order.filled_quantity})")
print(f"  Type:     {order.order_type} / {order.time_in_force}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |
| `order_id` | `str` | The unique order identifier to retrieve |

**Returns:** `Order`

**Raises:** `NotFoundError` if the order does not exist or is not from today.

> **Implementation note:** Uses the singular path `GET /accounts/{id}/order/{orderId}`, consistent with the `create_order` endpoint.

---

### `list_orders(account_id: str) -> list[Order]`

Returns all orders for the current trading day (all statuses: open, filled, cancelled).

```python
orders = client.trading.list_orders("ABC123")

for order in orders:
    print(f"{order.client_order_id} | {order.symbol} | {order.side}")
    print(f"  Status:   {order.order_status}")
    print(f"  Qty:      {order.quantity} (filled: {order.filled_quantity})")
    print(f"  Avg fill: {order.average_price}")
    print(f"  Type:     {order.order_type} / {order.time_in_force}")
    if order.limit_price:
        print(f"  Limit:    {order.limit_price}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |

**Returns:** `list[Order]`

---

### `list_historical_orders(account_id: str, start_date: str) -> list[TradeRecord]`

Returns historical executed trades starting from `start_date`. The API returns up to one week of data per request.

```python
from datetime import datetime, timedelta

# Trades from the last 7 days
start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
trades = client.trading.list_historical_orders("ABC123", start_date=start)

for trade in trades:
    print(f"{trade.trade_date} | {trade.symbol} | {trade.side} | {trade.qty} @ {trade.price}")
    print(f"  Net proceeds: {trade.net_proceeds:.2f}")
    print(f"  Commission:   {trade.commission:.2f}")
    print(f"  Cancelled:    {trade.canceled}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |
| `start_date` | `str` | Start date in `YYYY-MM-DD` format |

**Returns:** `list[TradeRecord]`

> **Note:** The API uses a path-parameter URL: `GET /accounts/{id}/orders/start-date/{startDate}`

---

### `list_historical_orders_paginated(account_id: str, start_date: str, *, page: int | None = None, page_size: int | None = None) -> PaginatedTradeResponse`

Returns up to **one year** of historical trade records with pagination support. Use this instead of `list_historical_orders` when you need data beyond one week or want to page through large result sets.

Only available for live production accounts — paper trading accounts are not supported.

```python
from datetime import datetime, timedelta

# Trades from the last 90 days, first page of 100
start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
result = client.trading.list_historical_orders_paginated(
    "ABC123", start_date=start, page=1, page_size=100
)

print(f"Page {result.page} — {len(result.trades)} trades (total: {result.total_count})")
for trade in result.trades:
    print(f"  {trade.trade_date} | {trade.symbol} | {trade.qty} @ {trade.price}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |
| `start_date` | `str` | Start date in `YYYY-MM-DD` format |
| `page` | `int \| None` | Page number to retrieve (1-based). Omitted if `None`. |
| `page_size` | `int \| None` | Records per page. Omitted if `None`. |

**Returns:** `PaginatedTradeResponse` — contains `trades: list[TradeRecord]` and optional `page`, `page_size`, `total_count` fields.

> **Note:** Uses path `GET /accounts/{id}/orders-with-pagination/start-date/{startDate}`. Pagination query params are forwarded as `page` and `pageSize` when provided.

---

### `cancel_order(account_id: str, client_order_id: str) -> None`

Cancels a specific open order by its client order ID.

```python
client.trading.cancel_order("ABC123", "my-order-001")
# Returns None on success
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |
| `client_order_id` | `str` | The `clientOrderId` from `create_order` or `list_orders` |

**Returns:** `None`

**Raises:** `NotFoundError` if the order does not exist or is already filled/cancelled.

---

### `cancel_all_orders(account_id: str, *, symbol: str | None = None) -> dict | None`

Cancels all open orders for an account. Optionally filter by symbol.

```python
# Cancel all open orders
client.trading.cancel_all_orders("ABC123")

# Cancel only AAPL orders
client.trading.cancel_all_orders("ABC123", symbol="AAPL")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier (sent in form body) |
| `symbol` | `str \| None` | Optional — filter cancellations to this symbol |

**Returns:** `dict | None` — API confirmation response or `None` on empty body.

> **Implementation note:** `account_id` is sent as form-encoded data in the request body, not as a URL parameter. `symbol` is sent as a query string parameter.

---

### `is_easy_to_borrow(account_id: str, symbol: str) -> bool`

Checks whether a symbol is on the easy-to-borrow list for short selling. Use this before attempting a short order to determine if a locate is required.

```python
etb = client.trading.is_easy_to_borrow("ABC123", "AAPL")
if etb:
    print("AAPL can be shorted without a locate")
else:
    print("AAPL requires a locate — use client.locates.request_quote()")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |
| `symbol` | `str` | Ticker symbol to check |

**Returns:** `bool` — `True` if easy to borrow, `False` otherwise.

---

### `get_routes(account_id: str) -> list[dict]`

Returns the list of available trading routes for an account. Route names can be passed to `create_order(route=...)`.

```python
routes = client.trading.get_routes("ABC123")
for route in routes:
    print(route)  # dict — structure varies by broker configuration
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |

**Returns:** `list[dict]` — raw dicts (route schema is not standardized in the API docs).

---

## 8. Locates Module

Accessible as `client.locates`.

Locates are required before short-selling stocks that are not easy-to-borrow. The locate workflow is:

```
1. request_quote()   →  submit locate request (status: NEW)
2. get_history()     →  poll until status == OFFERED (or REJECTED/EXPIRED)
3. accept_quote()    →  accept the offered rate
4. [trade]           →  place your short sell order
5. sell_locate()     →  return unused inventory for credit (optional)
6. cancel_locate()   →  cancel a pending request (optional)
```

---

### `request_quote(account, symbol, quantity, quote_req_id) -> dict`

Submits a locate quote request for a specified number of shares.

```python
import uuid

quote_req_id = str(uuid.uuid4())  # unique identifier you generate

response = client.locates.request_quote(
    account="ABC123",
    symbol="GME",
    quantity=500,
    quote_req_id=quote_req_id,
)
print(response)  # raw dict acknowledgement
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account` | `str` | Account ID requesting the locate |
| `symbol` | `str` | Ticker symbol to locate |
| `quantity` | `int` | Number of shares to locate (> 0) |
| `quote_req_id` | `str` | Unique client-generated request identifier |

**Returns:** `dict` — raw API acknowledgement.

---

### `get_history(account_id: str) -> list[LocateHistoryItem]`

Returns the history of locate requests for the day. Use this to poll for the status of a `request_quote()` call.

```python
import time
from tradezero.enums import LocateStatus

quote_req_id = "my-locate-001"

# Poll until offered or terminal state
while True:
    history = client.locates.get_history("ABC123")
    item = next((h for h in history if h.quote_req_id == quote_req_id), None)

    if item is None:
        print("Not found yet")
    elif item.locate_status == LocateStatus.OFFERED:
        print(f"Offered! Rate: {item.rate}")
        break
    elif item.locate_status in (LocateStatus.REJECTED, LocateStatus.EXPIRED, LocateStatus.CANCELED):
        print(f"Terminal status: {item.locate_status.name}")
        break
    else:
        print(f"Current status: {item.locate_status.name} — waiting...")

    time.sleep(2)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |

**Returns:** `list[LocateHistoryItem]`

**`LocateStatus` values:**

| Status | Value | Meaning |
|--------|-------|---------|
| `NEW` | 48 | Request submitted, not yet processed |
| `QUOTING` | 81 | Being priced by the locate desk |
| `OFFERED` | 65 | A rate has been offered — ready to accept |
| `FILLED` | 50 | Locate accepted and inventory allocated |
| `PENDING` | 54 | Pending processing |
| `CANCELED` | 52 | Canceled by client or system |
| `REJECTED` | 56 | Rejected by the locate desk |
| `EXPIRED` | 67 | Offer expired before acceptance |

---

### `get_inventory(account_id: str) -> list[LocateInventoryItem]`

Returns the current locate inventory — shares you have already located and are holding.

```python
inventory = client.locates.get_inventory("ABC123")

for item in inventory:
    print(f"Available: {item.available}")
    print(f"Sold:      {item.sold}")
    print(f"Unavail:   {item.unavailable}")
    print(f"Type:      {item.locate_type}")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |

**Returns:** `list[LocateInventoryItem]`

---

### `accept_quote(account_id: str, quote_req_id: str) -> dict`

Accepts an offered locate quote. Call this only after `get_history()` shows `LocateStatus.OFFERED`.

```python
response = client.locates.accept_quote("ABC123", "my-locate-001")
print(response)  # raw dict confirmation
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |
| `quote_req_id` | `str` | The identifier from your `request_quote()` call |

**Returns:** `dict` — raw API confirmation.

**Raises:** `TradeZeroAPIError` if the quote is no longer in OFFERED state.

---

### `sell_locate(account, symbol, quote_req_id, quantity, locate_type) -> dict`

Credits back locate inventory that you no longer need.

```python
from tradezero.enums import LocateTypeStr

response = client.locates.sell_locate(
    account="ABC123",
    symbol="GME",
    quote_req_id="my-sell-locate-001",
    quantity=200,
    locate_type=LocateTypeStr.LOCATE,  # or "Locate"
)
print(response)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account` | `str` | Account ID |
| `symbol` | `str` | Ticker symbol |
| `quote_req_id` | `str` | New unique identifier for this sell action |
| `quantity` | `int` | Shares to credit back (must be ≤ available) |
| `locate_type` | `LocateTypeStr \| str` | Locate type (e.g., `"Locate"`, `"IntraDay"`) |

**Returns:** `dict` — raw API confirmation.

---

### `cancel_locate(account_id: str, quote_req_id: str) -> None`

Cancels a pending locate request. Only valid while the request is in a cancelable state (NEW, QUOTING, PENDING).

```python
client.locates.cancel_locate("ABC123", "my-locate-001")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `account_id` | `str` | The account identifier |
| `quote_req_id` | `str` | The identifier of the locate to cancel |

**Returns:** `None`

---

## 9. Data Models

All models use Pydantic v2 with `populate_by_name=True` and `extra="ignore"` (unknown fields from the API are silently dropped). Fields accept both their Python snake_case names and their original API camelCase aliases.

---

### `Account`

Full account record. Returned by `list_accounts()` and `get_account_details()`.

| Field | Type | API Alias | Description |
|-------|------|-----------|-------------|
| `account` | `str` | `account` / `accountId` | Unique account identifier |
| `account_status` | `str \| None` | `accountStatus` | Account status (e.g., `"Active"`) |
| `available_cash` | `float` | `availableCash` | Cash available for trading |
| `buying_power` | `float` | `buyingPower` | Total buying power including leverage |
| `equity` | `float` | `equity` | Total equity value |
| `leverage` | `float` | `leverage` | Maximum leverage ratio |
| `overnight_bp` | `float` | `overnightBp` | Overnight buying power |
| `realized` | `float` | `realized` | Realized P&L |
| `shares_traded` | `float` | `sharesTraded` | Total shares traded |
| `sod_equity` | `float` | `sodEquity` | Start-of-day equity |
| `total_commissions` | `float` | `totalCommissions` | Total commissions paid |
| `total_locate_costs` | `float` | `totalLocateCosts` | Total locate costs |
| `used_leverage` | `float` | `usedLeverage` | Current leverage in use |
| `opt_contracts_traded` | `float` | `optContractsTraded` | Option contracts traded |
| `opt_level` | `float` | `optLevel` | Options trading tier |
| `option_cash_total_balance` | `float` | `optionCashTotalBalance` | Cash allocated to options |
| `option_trading_level` | `float` | `optionTradingLevel` | Options authorization level |

---

### `AccountPnL`

Daily P&L and balance metrics. Returned by `get_account_pnl()`.

| Field | Type | API Alias | Description |
|-------|------|-----------|-------------|
| `account_value` | `float` | `accountValue` | Total account value |
| `allowed_leverage` | `float` | `allowedLeverage` | Maximum leverage permitted |
| `available_cash` | `float` | `availableCash` | Cash available |
| `day_pnl` | `float` | `dayPnl` | Total day P&L |
| `day_realized` | `float` | `dayRealized` | Day realized P&L |
| `day_unrealized` | `float` | `dayUnrealized` | Day unrealized P&L |
| `equity_ratio` | `float` | `equityRatio` | Equity / account value ratio |
| `exposure` | `float` | `exposure` | Total market exposure |
| `option_cash_used` | `float` | `optionCashUsed` | Cash used for options |
| `pnl` | `list[dict]` | `pnl` | Detailed P&L breakdown (raw) |
| `shares_traded` | `float` | `sharesTraded` | Shares traded today |
| `total_unrealized` | `float` | `totalUnrealized` | Total unrealized P&L |
| `used_leverage` | `float` | `usedLeverage` | Current leverage ratio |

---

### `OrderResponse`

Returned immediately after `create_order()`.

| Field | Type | API Alias | Description |
|-------|------|-----------|-------------|
| `account_id` | `str` | `accountId` | Account the order was sent on |
| `order_status` | `str` | `orderStatus` | Status (e.g., `"Pending"`, `"Filled"`) |
| `executed` | `float` | `executed` | Quantity already executed |
| `leaves_quantity` | `float` | `leavesQuantity` | Remaining quantity to fill |
| `price_avg` | `float` | `priceAvg` | Average fill price |
| `last_updated` | `str \| None` | `lastUpdated` | Timestamp of last update |
| `text` | `str \| None` | `text` | Exchange message or error |
| `margin_requirement` | `float` | `marginRequirement` | Margin required for this order |

---

### `Order`

Full order record from `list_orders()`.

| Field | Type | API Alias | Description |
|-------|------|-----------|-------------|
| `client_order_id` | `str` | `clientOrderId` | Your order reference ID |
| `symbol` | `str` | `symbol` / `tradedSymbol` | Ticker symbol |
| `side` | `str` | `side` | `"Buy"` or `"Sell"` |
| `quantity` | `int` | `quantity` / `orderQuantity` | Requested quantity |
| `order_type` | `str` | `orderType` | Execution style |
| `time_in_force` | `str` | `timeInForce` | Duration instruction |
| `order_status` | `str` | `orderStatus` | Current lifecycle status |
| `filled_quantity` | `int` | `filledQuantity` | Executed quantity so far |
| `average_price` | `float` | `averagePrice` | Average fill price |
| `limit_price` | `float \| None` | `limitPrice` | Limit price if applicable |
| `stop_price` | `float \| None` | `stopPrice` | Stop price if applicable |

---

### `TradeRecord`

Historical trade from `list_historical_orders()`.

| Field | Type | API Alias | Description |
|-------|------|-----------|-------------|
| `account_id` | `str` | `accountId` | Account identifier |
| `trade_id` | `int` | `tradeId` | Unique trade ID |
| `symbol` | `str` | `symbol` | Ticker symbol |
| `qty` | `int` | `qty` | Quantity traded |
| `price` | `float` | `price` | Execution price |
| `side` | `str \| None` | `side` | `"Buy"` / `"Sell"` or `None` |
| `trade_date` | `str` | `tradeDate` | Trade date (ISO 8601) |
| `settle_date` | `str` | `settleDate` | Settlement date (ISO 8601) |
| `entry_date` | `str` | `entryDate` | Entry date (ISO 8601) |
| `exec_time` | `str \| None` | `execTime` | Execution time |
| `gross_proceeds` | `float` | `grossProceeds` | Gross proceeds |
| `net_proceeds` | `float` | `netProceeds` | Net proceeds after fees |
| `commission` | `float` | `commission` | Commission charged |
| `total_fees` | `float \| None` | `totalFees` | Total fees |
| `canceled` | `bool` | `canceled` | Whether the trade was cancelled |
| `currency` | `str` | `currency` | Trade currency |
| `security_type` | `str \| None` | `securityType` | Security type if available |
| `notes` | `str \| None` | `notes` | Additional notes |

---

### `Position`

Open position with computed unrealized P&L. Returned by `get_positions()`.

| Field | Type | API Alias | Description |
|-------|------|-----------|-------------|
| `symbol` | `str` | `symbol` | Ticker symbol |
| `shares` | `int` | `shares` | Number of shares |
| `side` | `str` | `side` | `"Long"` or `"Short"` |
| `price_avg` | `float` | `priceAvg` | Average entry price |
| `price_close` | `float` | `priceClose` | Current/last price |
| `day_overnight` | `str` | `dayOvernight` | Position type indicator |
| `unrealized_pnl` | `float` | _(computed)_ | Calculated P&L (not from API) |

---

### `LocateHistoryItem`

Single locate history record from `get_history()`.

| Field | Type | API Alias | Description |
|-------|------|-----------|-------------|
| `quote_req_id` | `str` | `quoteReqID` | Request identifier |
| `symbol` | `str` | `symbol` | Ticker symbol |
| `quantity` | `int \| None` | `quantity` | Requested quantity |
| `locate_status` | `LocateStatus` | `locateStatus` | Status code (see [LocateStatus](#locatestatus)) |
| `rate` | `float` | `rate` | Offered borrow rate |

---

### `LocateInventoryItem`

Single inventory record from `get_inventory()`.

| Field | Type | API Alias | Description |
|-------|------|-----------|-------------|
| `available` | `int` | `available` | Shares available to borrow |
| `sold` | `int` | `sold` | Shares already borrowed |
| `unavailable` | `int` | `unavailable` | Shares that cannot be located |
| `locate_type` | `int` | `locateType` | Integer type code |

---

## 10. Enumerations

Import enums from `tradezero.enums`:

```python
from tradezero.enums import (
    OrderSide, OrderType, TimeInForce, SecurityType,
    LocateStatus, LocateTypeStr,
)
```

### `OrderSide`

| Member | Wire Value | Description |
|--------|-----------|-------------|
| `OrderSide.BUY` | `"Buy"` | Buy order |
| `OrderSide.SELL` | `"Sell"` | Sell or short-sell order |

### `OrderType`

| Member | Wire Value | Description |
|--------|-----------|-------------|
| `OrderType.MARKET` | `"Market"` | Execute at best available price |
| `OrderType.LIMIT` | `"Limit"` | Execute only at `limit_price` or better |
| `OrderType.STOP` | `"Stop"` | Market order triggered at `stop_price` |
| `OrderType.STOP_LIMIT` | `"StopLimit"` | Limit order triggered at `stop_price` |

### `TimeInForce`

| Member | Wire Value | Description |
|--------|-----------|-------------|
| `TimeInForce.DAY` | `"Day"` | Cancel at end of regular session |
| `TimeInForce.GTC` | `"GoodTillCancel"` | Remain open until explicitly cancelled |
| `TimeInForce.IOC` | `"ImmediateOrCancel"` | Fill immediately; cancel any remainder |
| `TimeInForce.FOK` | `"FillOrKill"` | Fill completely or cancel entirely |
| `TimeInForce.AT_THE_OPENING` | `"AtTheOpening"` | Execute at the opening only |
| `TimeInForce.GOOD_TILL_CROSSING` | `"GoodTillCrossing"` | Valid until market crossing |
| `TimeInForce.DAY_PLUS` | `"Day_Plus"` | Day order including extended hours |
| `TimeInForce.GTC_PLUS` | `"GTC_Plus"` | GTC including extended hours |

### `SecurityType`

| Member | Wire Value | Description |
|--------|-----------|-------------|
| `SecurityType.STOCK` | `"Stock"` | Equity security (default) |
| `SecurityType.OPTION` | `"Option"` | Options contract |

### `LocateStatus`

Integer status codes returned in locate history (FIX protocol style).

| Member | Integer Value | Description |
|--------|--------------|-------------|
| `LocateStatus.NEW` | 48 | Request submitted |
| `LocateStatus.FILLED` | 50 | Locate accepted and filled |
| `LocateStatus.CANCELED` | 52 | Cancelled |
| `LocateStatus.PENDING` | 54 | Pending processing |
| `LocateStatus.REJECTED` | 56 | Rejected by locate desk |
| `LocateStatus.OFFERED` | 65 | Rate offered — ready to accept |
| `LocateStatus.EXPIRED` | 67 | Offer expired |
| `LocateStatus.QUOTING` | 81 | Being priced |

### `LocateTypeStr`

| Member | Wire Value | Description |
|--------|-----------|-------------|
| `LocateTypeStr.UNKNOWN` | `"Unknown"` | Unknown type |
| `LocateTypeStr.LOCATE` | `"Locate"` | Standard locate |
| `LocateTypeStr.INTRADAY` | `"IntraDay"` | Intraday locate |
| `LocateTypeStr.PRE_BORROW` | `"PreBorrow"` | Pre-borrow arrangement |
| `LocateTypeStr.SINGLE_USE` | `"SingleUse"` | Single-use locate |

### String Coercion

All methods accept either the enum member or the raw string value interchangeably:

```python
# These are all equivalent:
client.trading.create_order(..., side=OrderSide.BUY, ...)
client.trading.create_order(..., side="Buy", ...)
```

---

## 11. Exception Handling

All SDK exceptions are importable from the `tradezero` namespace:

```python
from tradezero import (
    TradeZeroSDKError,
    TradeZeroAPIError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    APIValidationError,
    InsufficientFundsError,
    ServerError,
)
```

### Exception Hierarchy

```
Exception
└── TradeZeroSDKError          — base for all SDK errors
    └── TradeZeroAPIError      — non-2xx HTTP response
        ├── AuthenticationError    (HTTP 401)
        ├── ForbiddenError         (HTTP 403)
        ├── NotFoundError          (HTTP 404)
        ├── RateLimitError         (HTTP 429)  ← auto-retried
        ├── APIValidationError     (HTTP 422)
        ├── InsufficientFundsError (custom business logic)
        └── ServerError            (HTTP 5xx)  ← auto-retried
```

### `TradeZeroAPIError` Attributes

All API errors carry these extra attributes for debugging:

| Attribute | Type | Description |
|-----------|------|-------------|
| `status_code` | `int \| None` | HTTP status code |
| `response_body` | `str \| None` | Raw response body text |

```python
try:
    client.trading.create_order(...)
except TradeZeroAPIError as e:
    print(e.status_code)    # e.g. 422
    print(e.response_body)  # e.g. '{"message": "Invalid symbol"}'
    print(str(e))           # full message including URL
```

### Catch Patterns

**Catch a specific error:**
```python
from tradezero import AuthenticationError

try:
    client.accounts.list_accounts()
except AuthenticationError:
    print("Invalid API credentials — check TZ_API_KEY and TZ_API_SECRET")
```

**Catch any API error:**
```python
from tradezero import TradeZeroAPIError

try:
    client.trading.create_order(...)
except TradeZeroAPIError as e:
    print(f"API error {e.status_code}: {e}")
```

**Catch everything from this SDK:**
```python
from tradezero import TradeZeroSDKError

try:
    client.accounts.list_accounts()
except TradeZeroSDKError as e:
    print(f"SDK error: {e}")
```

**Full production pattern:**
```python
from tradezero import (
    AuthenticationError, InsufficientFundsError,
    RateLimitError, TradeZeroAPIError, TradeZeroSDKError,
)

try:
    resp = client.trading.create_order(
        account_id, "AAPL", 100, "Buy", "Limit", "Day", limit_price=185.0
    )
except AuthenticationError:
    # Credentials are wrong — no point retrying
    raise SystemExit("Fatal: invalid API credentials")
except InsufficientFundsError:
    print("Not enough buying power")
except RateLimitError:
    # SDK already retried 3 times — back off for longer
    print("Still rate-limited after 3 retries")
except TradeZeroAPIError as e:
    print(f"Unexpected API error {e.status_code}: {e}")
except TradeZeroSDKError as e:
    print(f"SDK error: {e}")
```

---

## 12. Retry Behaviour

The SDK uses [Tenacity](https://tenacity.readthedocs.io/) to automatically retry failed requests.

### Policy

| Condition | Behaviour |
|-----------|-----------|
| `RateLimitError` (HTTP 429) | Retried automatically |
| `ServerError` (HTTP 5xx) | Retried automatically |
| `httpx.TransportError` (network) | Retried automatically |
| `AuthenticationError` (401) | **Not retried** |
| `ForbiddenError` (403) | **Not retried** |
| `NotFoundError` (404) | **Not retried** |
| `APIValidationError` (422) | **Not retried** |
| `InsufficientFundsError` | **Not retried** |

### Backoff Schedule

| Attempt | Wait before retry |
|---------|-------------------|
| 1st failure | 1 second |
| 2nd failure | 2 seconds |
| 3rd failure | 4 seconds |
| 4th failure | Raises exception |

Maximum wait is capped at 60 seconds. After 3 retries the original exception is raised to the caller.

### Disabling Retries

There is no built-in toggle, but you can catch and handle errors yourself or wrap calls in your own retry logic if you need different behaviour.

---

## 13. Async Usage

Every method available on the sync client has an identical async counterpart. All you need to change is:

1. Use `AsyncTradeZeroClient` instead of `TradeZeroClient`
2. Use `async with` instead of `with`
3. `await` every method call

```python
import asyncio
from tradezero import AsyncTradeZeroClient

async def trading_workflow():
    async with AsyncTradeZeroClient(api_key="...", api_secret="...") as client:
        # All module methods are identical — just awaited
        accounts = await client.accounts.list_accounts()
        account_id = accounts[0].account

        pnl = await client.accounts.get_account_pnl(account_id)
        positions = await client.positions.get_positions(account_id)

        resp = await client.trading.create_order(
            account_id, "AAPL", 50, "Buy", "Market", "Day"
        )
        await client.trading.cancel_order(account_id, resp_client_order_id)

asyncio.run(trading_workflow())
```

### Parallel requests with `asyncio.gather`

```python
import asyncio
from tradezero import AsyncTradeZeroClient

async def fetch_all(account_id: str):
    async with AsyncTradeZeroClient() as client:
        # Run multiple requests concurrently
        accounts, positions, orders = await asyncio.gather(
            client.accounts.list_accounts(),
            client.positions.get_positions(account_id),
            client.trading.list_orders(account_id),
        )
        return accounts, positions, orders
```

### Using with FastAPI

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from tradezero import AsyncTradeZeroClient

client: AsyncTradeZeroClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = AsyncTradeZeroClient()
    yield
    await client.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/accounts")
async def get_accounts():
    return await client.accounts.list_accounts()
```

---

## 14. Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `TZ_API_KEY` | TradeZero API key ID | — (required if not passed to constructor) |
| `TZ_API_SECRET` | TradeZero API secret key | — (required if not passed to constructor) |
| `TZ_BASE_URL` | Override the API base URL | `https://webapi.tradezero.com/v1/api` |

```bash
# Linux / macOS / WSL
export TZ_API_KEY="your-key"
export TZ_API_SECRET="your-secret"

# Windows CMD
set TZ_API_KEY=your-key
set TZ_API_SECRET=your-secret

# Windows PowerShell
$env:TZ_API_KEY="your-key"
$env:TZ_API_SECRET="your-secret"
```

---

## 15. Package Structure

```
tradezero-sdk/
│
├── tradezero/                          # Main installable package
│   ├── __init__.py                     # Public API surface & __version__
│   ├── config.py                       # Constants and env-var helpers
│   ├── enums.py                        # All API enumerations
│   ├── exceptions.py                   # Exception hierarchy & raise_for_status()
│   │
│   ├── client/
│   │   ├── __init__.py                 # Re-exports TradeZeroClient, AsyncTradeZeroClient
│   │   ├── sync_client.py              # TradeZeroClient (synchronous)
│   │   └── async_client.py             # AsyncTradeZeroClient (asynchronous)
│   │
│   ├── http/
│   │   ├── __init__.py                 # Re-exports SyncHTTPClient, AsyncHTTPClient
│   │   ├── _base.py                    # build_auth_headers(), strip_none()
│   │   ├── _retry.py                   # Tenacity sdk_retry decorator
│   │   ├── sync_http.py                # SyncHTTPClient (httpx.Client)
│   │   └── async_http.py               # AsyncHTTPClient (httpx.AsyncClient)
│   │
│   ├── models/
│   │   ├── __init__.py                 # Re-exports all Pydantic models
│   │   ├── accounts.py                 # Account, AccountPnL
│   │   ├── orders.py                   # CreateOrderRequest, OrderResponse,
│   │   │                               # Order, TradeRecord
│   │   ├── positions.py                # Position (with computed unrealized_pnl)
│   │   └── locates.py                  # LocateQuoteRequest, LocateAcceptRequest,
│   │                                   # LocateSellRequest, LocateInventoryItem,
│   │                                   # LocateHistoryItem
│   │
│   └── modules/
│       ├── __init__.py                 # Re-exports all sync & async module classes
│       ├── accounts.py                 # AccountsModule, AsyncAccountsModule
│       ├── trading.py                  # TradingModule, AsyncTradingModule
│       ├── positions.py                # PositionsModule, AsyncPositionsModule
│       └── locates.py                  # LocatesModule, AsyncLocatesModule
│
├── tests/
│   ├── conftest.py                     # Shared pytest fixtures (mock_router)
│   ├── test_accounts.py                # AccountsModule unit tests
│   ├── test_trading.py                 # TradingModule unit tests
│   ├── test_positions.py               # PositionsModule unit tests
│   ├── test_locates.py                 # LocatesModule unit tests
│   ├── test_async.py                   # AsyncTradeZeroClient unit tests
│   ├── test_exceptions.py              # Exception hierarchy tests
│   ├── test_retry.py                   # Retry logic tests
│   └── live/                           # Live integration tests (require real API)
│       ├── conftest.py                 # Live fixtures (reads TZ_API_KEY / TZ_API_SECRET)
│       ├── test_accounts.py
│       ├── test_trading.py
│       ├── test_positions.py
│       ├── test_locates.py
│       └── test_errors.py
│
├── examples/
│   ├── basic_sync.py                   # Synchronous usage example
│   └── basic_async.py                  # Asynchronous usage example
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       └── ci.yml                      # CI: lint + typecheck + test (Python 3.11, 3.12)
│
├── README.md                           # Quick start and overview
├── DOCUMENTATION.md                    # This file — complete reference
├── CONTRIBUTING.md                     # Contributor guide
├── CHANGELOG.md                        # Version history
├── SECURITY.md                         # Security policy
├── LICENSE                             # MIT License
├── pyproject.toml                      # Package metadata and tool configuration
└── pytest.ini                          # Pytest configuration
```

---

*To sponsor the project: [PayPal](https://www.paypal.me/shaadyemad) · Binance Pay UID: `751730419`*

*For questions or support contact [ShadyEmadContact@gmail.com](mailto:ShadyEmadContact@gmail.com)*
*or open an issue at [github.com/shadyemad/tradezero-sdk/issues](https://github.com/shadyemad/tradezero-sdk/issues).*
