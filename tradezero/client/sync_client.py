"""Synchronous top-level TradeZero client."""

from __future__ import annotations

import os
from typing import Any

from tradezero.config import (
    DEFAULT_TIMEOUT,
    base_url_from_env,
    api_key_from_env,
    api_secret_from_env,
)
from tradezero.http.sync_http import SyncHTTPClient
from tradezero.modules.accounts import AccountsModule
from tradezero.modules.trading import TradingModule
from tradezero.modules.positions import PositionsModule
from tradezero.modules.locates import LocatesModule


class TradeZeroClient:
    """Synchronous entry-point for the TradeZero SDK.

    Instantiate once and reuse across calls. Supports context-manager usage
    to automatically release HTTP connections::

        with TradeZeroClient(api_key="...", api_secret="...") as client:
            accounts = client.accounts.list_accounts()

    Args:
        api_key: TradeZero API key ID.  Falls back to the ``TZ_API_KEY``
            environment variable if omitted.
        api_secret: TradeZero API secret key.  Falls back to ``TZ_API_SECRET``.
        base_url: Override the default base URL.  Falls back to ``TZ_BASE_URL``
            or ``https://webapi.tradezero.com/v1/api``.
        timeout: Per-request timeout in seconds (default: 30).

    Attributes:
        accounts: :class:`~tradezero.modules.accounts.AccountsModule`
        trading: :class:`~tradezero.modules.trading.TradingModule`
        positions: :class:`~tradezero.modules.positions.PositionsModule`
        locates: :class:`~tradezero.modules.locates.LocatesModule`

    Raises:
        ValueError: If neither keyword arguments nor environment variables
            supply the required credentials.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        resolved_key = api_key or api_key_from_env()
        resolved_secret = api_secret or api_secret_from_env()
        resolved_url = base_url or base_url_from_env()

        if not resolved_key:
            raise ValueError(
                "api_key is required. Pass it explicitly or set the TZ_API_KEY "
                "environment variable."
            )
        if not resolved_secret:
            raise ValueError(
                "api_secret is required. Pass it explicitly or set the TZ_API_SECRET "
                "environment variable."
            )

        self._http = SyncHTTPClient(
            api_key=resolved_key,
            api_secret=resolved_secret,
            base_url=resolved_url,
            timeout=timeout,
        )

        # Domain modules
        self.accounts = AccountsModule(self._http)
        self.trading = TradingModule(self._http)
        self.positions = PositionsModule(self._http)
        self.locates = LocatesModule(self._http)

    def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> "TradeZeroClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
