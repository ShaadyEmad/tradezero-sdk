# Contributing to tradezero-sdk

Thank you for your interest in contributing! This guide will help you get set up.

## Development setup

```bash
git clone https://github.com/shadyemad/tradezero-sdk.git
cd tradezero-sdk

# Install Poetry if you don't have it
pip install poetry

# Install all dependencies (including dev)
poetry install
```

## Running tests

```bash
# Run unit tests only (no live API required)
poetry run pytest -m "not live" -v

# Run with coverage report
poetry run pytest -m "not live" --cov=tradezero --cov-report=term-missing

# Run live integration tests (requires TZ_API_KEY and TZ_API_SECRET environment variables)
poetry run pytest -m live -v
```

## Linting and type checking

```bash
# Lint with ruff
poetry run ruff check .

# Auto-fix ruff issues where possible
poetry run ruff check . --fix

# Type-check with mypy
poetry run mypy tradezero
```

All three commands must pass with zero errors before a PR can be merged.

## Project structure

```
tradezero/
├── __init__.py          # Public API surface
├── config.py            # Constants and env-var loaders
├── enums.py             # API enumerations
├── exceptions.py        # Exception hierarchy
├── http/
│   ├── _base.py         # Auth headers, query-param utils
│   ├── _retry.py        # Tenacity retry decorator
│   ├── sync_http.py     # Synchronous HTTP client
│   └── async_http.py    # Asynchronous HTTP client
├── models/
│   ├── accounts.py      # Account, AccountPnL
│   ├── orders.py        # CreateOrderRequest, OrderResponse, Order, TradeRecord
│   ├── positions.py     # Position (with computed unrealized_pnl)
│   └── locates.py       # Locate request/response models
├── modules/
│   ├── accounts.py      # AccountsModule + AsyncAccountsModule
│   ├── trading.py       # TradingModule + AsyncTradingModule
│   ├── positions.py     # PositionsModule + AsyncPositionsModule
│   └── locates.py       # LocatesModule + AsyncLocatesModule
└── client/
    ├── sync_client.py   # TradeZeroClient
    └── async_client.py  # AsyncTradeZeroClient
```

## Adding a new endpoint

1. Check the official TradeZero API documentation for the exact request/response structure.
2. Add or update Pydantic models in `tradezero/models/`.
3. Add the method to both the sync and async module classes in `tradezero/modules/`.
4. Add unit tests with mocked HTTP responses in `tests/`.
5. Update `CHANGELOG.md` under `[Unreleased]`.

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `fix: correct cancel_all_orders form body`
- `feat: add is_easy_to_borrow endpoint`
- `test: add retry logic unit tests`
- `docs: update README quickstart for v0.2`
- `chore: bump pydantic to 2.8`

## Submitting a pull request

1. Fork the repository and create a feature branch from `main`.
2. Make your changes, following the coding conventions in existing files.
3. Ensure all tests pass: `poetry run pytest -m "not live"`.
4. Ensure ruff and mypy pass with zero errors.
5. Coverage must not drop below the threshold in `pyproject.toml`.
6. Open a pull request with a clear description of the change and reference
   any relevant API documentation or GitHub issue numbers.

## Reporting issues

Please use [GitHub Issues](https://github.com/shadyemad/tradezero-sdk/issues) to report
bugs or request features. Include:
- The SDK version (`tradezero.__version__`)
- A minimal reproducible example
- The full traceback if applicable
