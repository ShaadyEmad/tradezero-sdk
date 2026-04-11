# tradezero-sdk

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/tradezero-sdk.svg)](https://pypi.org/project/tradezero-sdk/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/shadyemad/tradezero-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/shadyemad/tradezero-sdk/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/shadyemad/tradezero-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/shadyemad/tradezero-sdk)

An unofficial, production-ready Python SDK for the [TradeZero](https://www.tradezero.com/) REST API.

TradeZero is an online broker offering direct-access trading for equities. This SDK wraps their REST API with a clean Python interface — no manual HTTP, no raw JSON parsing, no retry boilerplate.

> **Disclaimer:** This is an unofficial, community-maintained library. It is not affiliated with, endorsed by, or supported by TradeZero Global Ltd. Use at your own risk. Always verify order execution through the official TradeZero platform before making financial decisions.

---

## Documentation & Links

| Resource | Description |
|----------|-------------|
| [DOCUMENTATION.md](DOCUMENTATION.md) | **Complete reference** — every class, method, model, enum, and exception explained in full |
| [CHANGELOG.md](CHANGELOG.md) | Full version history and breaking-change notes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to set up a dev environment and submit pull requests |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting policy and credential safety |
| [examples/basic_sync.py](examples/basic_sync.py) | Runnable synchronous usage example |
| [examples/basic_async.py](examples/basic_async.py) | Runnable asynchronous usage example |

---

## Features

- **Dual sync/async support** — `TradeZeroClient` for scripts, `AsyncTradeZeroClient` for async frameworks
- **Full Pydantic v2 validation** — all API responses parsed into typed Python models
- **Automatic retries with exponential backoff** — 429 and 5xx errors retried up to 3 times automatically
- **Rich exception hierarchy** — catch `AuthenticationError`, `RateLimitError`, `NotFoundError`, `ServerError`, and more
- **Environment variable support** — inject credentials via `TZ_API_KEY` / `TZ_API_SECRET`
- **Context-manager lifecycle** — connections released automatically via `with` / `async with`
- **Typed models for all resources** — accounts, P&L, positions, orders, trade history, and locates

---

## Installation

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

Requires **Python 3.11+**.

---

## Quick Start

### Synchronous

```python
from tradezero import TradeZeroClient

with TradeZeroClient(api_key="YOUR_KEY", api_secret="YOUR_SECRET") as client:
    # List all accounts
    accounts = client.accounts.list_accounts()
    account_id = accounts[0].account
    print(f"Account: {account_id}, Equity: {accounts[0].equity:,.2f}")

    # Get day P&L
    pnl = client.accounts.get_account_pnl(account_id)
    print(f"Day P&L: {pnl.day_pnl:+,.2f}, Realized: {pnl.day_realized:+,.2f}")

    # Open positions with computed unrealized P&L
    positions = client.positions.get_positions(account_id)
    for pos in positions:
        print(f"{pos.symbol} {pos.side}: unrealized = {pos.unrealized_pnl:+,.2f}")

    # Place a limit buy order
    resp = client.trading.create_order(
        account_id=account_id,
        symbol="AAPL",
        quantity=100,
        side="Buy",
        order_type="Limit",
        time_in_force="Day",
        limit_price=185.0,
    )
    print(f"Order status: {resp.order_status}")

    # Check short-sell borrow availability
    etb = client.trading.is_easy_to_borrow(account_id, "AAPL")
    print(f"AAPL easy to borrow: {etb}")

    # Cancel all open orders
    client.trading.cancel_all_orders(account_id)
```

### Asynchronous

```python
import asyncio
from tradezero import AsyncTradeZeroClient

async def main():
    async with AsyncTradeZeroClient(api_key="YOUR_KEY", api_secret="YOUR_SECRET") as client:
        accounts = await client.accounts.list_accounts()
        account_id = accounts[0].account

        pnl = await client.accounts.get_account_pnl(account_id)
        print(f"Day P&L: {pnl.day_pnl:+,.2f}")

        positions = await client.positions.get_positions(account_id)
        for pos in positions:
            print(f"{pos.symbol}: {pos.unrealized_pnl:+,.2f}")

        resp = await client.trading.create_order(
            account_id=account_id,
            symbol="TSLA",
            quantity=50,
            side="Sell",
            order_type="Market",
            time_in_force="Day",
        )
        print(f"Order: {resp.order_status}")

asyncio.run(main())
```

More complete examples are in the [`examples/`](examples/) directory.

---

## Configuration

Credentials can be passed explicitly or loaded from environment variables:

| Environment Variable | Description               | Default                               |
|----------------------|---------------------------|---------------------------------------|
| `TZ_API_KEY`         | TradeZero API key ID      | —                                     |
| `TZ_API_SECRET`      | TradeZero API secret key  | —                                     |
| `TZ_BASE_URL`        | Override the API base URL | `https://webapi.tradezero.com/v1/api` |

```bash
export TZ_API_KEY="your-key"
export TZ_API_SECRET="your-secret"
```

```python
# Credentials resolved automatically from environment
client = TradeZeroClient()
```

Additional constructor options:

```python
client = TradeZeroClient(
    api_key="...",
    api_secret="...",
    timeout=60.0,   # per-request timeout in seconds (default: 30)
)
```

---

## API Reference

> For full method signatures, parameter descriptions, return types, and code examples for every endpoint, see [DOCUMENTATION.md](DOCUMENTATION.md).

### `client.accounts`

| Method | Returns | Description |
|--------|---------|-------------|
| `list_accounts()` | `list[Account]` | All accounts for your API credentials |
| `get_account_details(account_id)` | `Account` | Full account details including all financial fields |
| `get_account_pnl(account_id)` | `AccountPnL` | Daily P&L, exposure, and balance metrics |

### `client.positions`

| Method | Returns | Description |
|--------|---------|-------------|
| `get_positions(account_id)` | `list[Position]` | All open positions with computed `unrealized_pnl` |

### `client.trading`

| Method | Returns | Description |
|--------|---------|-------------|
| `create_order(account_id, symbol, quantity, side, order_type, time_in_force, ...)` | `OrderResponse` | Place a new order |
| `list_orders(account_id)` | `list[Order]` | Current-day orders (all statuses) |
| `list_historical_orders(account_id, start_date)` | `list[TradeRecord]` | Trade records up to one week back |
| `cancel_order(account_id, client_order_id)` | `None` | Cancel a specific open order |
| `cancel_all_orders(account_id, *, symbol=None)` | `dict \| None` | Cancel all open orders, optionally filtered by symbol |
| `is_easy_to_borrow(account_id, symbol)` | `bool` | Check short-sell borrow availability |
| `get_routes(account_id)` | `list[dict]` | Available trading routes |

### `client.locates`

| Method | Returns | Description |
|--------|---------|-------------|
| `request_quote(account, symbol, quantity, quote_req_id)` | `dict` | Submit a short-sell locate quote request |
| `get_history(account_id)` | `list[LocateHistoryItem]` | Poll locate request history and status |
| `get_inventory(account_id)` | `list[LocateInventoryItem]` | Active locate inventory |
| `accept_quote(account_id, quote_req_id)` | `dict` | Accept an offered locate quote |
| `sell_locate(account, symbol, quote_req_id, quantity, locate_type)` | `dict` | Sell locate back for credit |
| `cancel_locate(account_id, quote_req_id)` | `None` | Cancel a pending locate quote |

---

## Enum Values

All enum values match the TradeZero API wire format exactly. String literals are accepted wherever enum members are — the SDK coerces them automatically:

```python
# These are equivalent:
client.trading.create_order(..., side="Buy", order_type="Limit", time_in_force="Day")
client.trading.create_order(..., side=OrderSide.BUY, order_type=OrderType.LIMIT, time_in_force=TimeInForce.DAY)
```

| Enum | Members |
|------|---------|
| `OrderSide` | `BUY="Buy"`, `SELL="Sell"` |
| `OrderType` | `MARKET="Market"`, `LIMIT="Limit"`, `STOP="Stop"`, `STOP_LIMIT="StopLimit"` |
| `TimeInForce` | `DAY="Day"`, `GTC="GoodTillCancel"`, `IOC="ImmediateOrCancel"`, `FOK="FillOrKill"`, `AT_THE_OPENING`, `GOOD_TILL_CROSSING`, `DAY_PLUS`, `GTC_PLUS` |
| `SecurityType` | `STOCK="Stock"`, `OPTION="Option"` |
| `LocateStatus` | `NEW=48`, `FILLED=50`, `CANCELED=52`, `PENDING=54`, `REJECTED=56`, `OFFERED=65`, `EXPIRED=67`, `QUOTING=81` |
| `LocateTypeStr` | `LOCATE="Locate"`, `INTRADAY="IntraDay"`, `PRE_BORROW="PreBorrow"`, `SINGLE_USE="SingleUse"` |

See [DOCUMENTATION.md § Enumerations](DOCUMENTATION.md#10-enumerations) for full descriptions of every member.

---

## Exception Handling

```python
from tradezero import (
    TradeZeroSDKError,       # Base class for all SDK errors
    TradeZeroAPIError,       # Non-2xx API response (.status_code, .response_body)
    AuthenticationError,     # 401 — invalid credentials
    ForbiddenError,          # 403 — insufficient permissions
    NotFoundError,           # 404 — resource not found
    RateLimitError,          # 429 — too many requests (auto-retried)
    APIValidationError,      # 422 — request validation failed
    InsufficientFundsError,  # insufficient buying power
    ServerError,             # 5xx — server error (auto-retried)
)

try:
    resp = client.trading.create_order(...)
except RateLimitError:
    print("Still rate limited after 3 automatic retries")
except AuthenticationError:
    print("Check your API credentials")
except InsufficientFundsError:
    print("Not enough buying power for this order")
except TradeZeroAPIError as e:
    print(f"API error {e.status_code}: {e}")
    print(f"Response body: {e.response_body}")
```

### Retry Behaviour

| Condition | Behaviour |
|-----------|-----------|
| `RateLimitError` (HTTP 429) | Retried up to 3 times |
| `ServerError` (HTTP 5xx) | Retried up to 3 times |
| `httpx.TransportError` (network) | Retried up to 3 times |
| All other errors | Raised immediately, no retry |

Backoff: 1 s → 2 s → 4 s, capped at 60 s.

---

## Package Structure

```
tradezero-sdk/
│
├── tradezero/                          # Main installable package
│   ├── __init__.py                     # Public API surface & __version__
│   ├── config.py                       # Constants and env-var helpers
│   ├── enums.py                        # All API enumerations
│   ├── exceptions.py                   # Exception hierarchy
│   ├── client/
│   │   ├── sync_client.py              # TradeZeroClient (synchronous)
│   │   └── async_client.py             # AsyncTradeZeroClient (asynchronous)
│   ├── http/
│   │   ├── _base.py                    # Auth headers, utility functions
│   │   ├── _retry.py                   # Tenacity retry decorator
│   │   ├── sync_http.py                # SyncHTTPClient
│   │   └── async_http.py               # AsyncHTTPClient
│   ├── models/
│   │   ├── accounts.py                 # Account, AccountPnL
│   │   ├── orders.py                   # CreateOrderRequest, OrderResponse,
│   │   │                               # Order, TradeRecord
│   │   ├── positions.py                # Position (with computed unrealized_pnl)
│   │   └── locates.py                  # All locate request/response models
│   └── modules/
│       ├── accounts.py                 # AccountsModule + AsyncAccountsModule
│       ├── trading.py                  # TradingModule + AsyncTradingModule
│       ├── positions.py                # PositionsModule + AsyncPositionsModule
│       └── locates.py                  # LocatesModule + AsyncLocatesModule
│
├── tests/
│   ├── conftest.py                     # Shared pytest fixtures
│   ├── test_accounts.py                # 7 unit tests
│   ├── test_trading.py                 # 14 unit tests
│   ├── test_positions.py               # 5 unit tests
│   ├── test_locates.py                 # 8 unit tests
│   ├── test_async.py                   # 11 unit tests
│   ├── test_exceptions.py              # 3 unit tests
│   ├── test_retry.py                   # 6 unit tests
│   └── live/                           # Live integration tests (real API, opt-in)
│       ├── conftest.py                 # Reads TZ_API_KEY / TZ_API_SECRET from env
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
│   └── workflows/ci.yml                # CI pipeline (Python 3.11 + 3.12)
│
├── README.md                           # This file
├── DOCUMENTATION.md                    # Complete reference documentation
├── CONTRIBUTING.md                     # Contributor guide
├── CHANGELOG.md                        # Version history
├── SECURITY.md                         # Security and vulnerability policy
├── LICENSE                             # MIT License
├── pyproject.toml                      # Package metadata, deps, tool config
└── pytest.ini                          # Pytest settings
```

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide.

```bash
# Install all dependencies including dev tools
poetry install

# Run unit tests (no API credentials required)
poetry run pytest -m "not live" --cov=tradezero -v

# Lint with ruff
poetry run ruff check .

# Type-check with mypy
poetry run mypy tradezero
```

Live integration tests (require real credentials):

```bash
export TZ_API_KEY="your-key"
export TZ_API_SECRET="your-secret"
poetry run pytest tests/live/ -m live -v
```

---

## Sponsorship

If this SDK saves you time or money, consider sponsoring the project:

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-00457C.svg?logo=paypal)](https://www.paypal.me/shaadyemad)

**Binance Pay** — UID: `751730419`

Your support helps maintain the library, add new endpoints, and test against the live API.

---

## Contact & Contributing

- **Email:** [ShadyEmadContact@gmail.com](mailto:ShadyEmadContact@gmail.com)
- **Issues & feature requests:** [GitHub Issues](https://github.com/shadyemad/tradezero-sdk/issues)
- **Pull requests:** Read [CONTRIBUTING.md](CONTRIBUTING.md) first

Contributions are welcome:

1. Fork the repository and create a feature branch from `main`
2. Make your change and add tests
3. Run `pytest -m "not live"`, `ruff check .`, and `mypy tradezero` — all must pass
4. Open a pull request with a clear description

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Shady Emad

---

> **Disclaimer:** tradezero-sdk is an unofficial, community-maintained project. It is not affiliated with, endorsed by, or sponsored by TradeZero Global Ltd. The TradeZero name and API are trademarks of TradeZero Global Ltd. The authors accept no responsibility for financial losses resulting from the use of this library. Always verify all trades through the official TradeZero platform.
