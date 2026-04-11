"""Asynchronous top-level TradeZero client."""

from __future__ import annotations

from typing import Any

from tradezero.config import (
    DEFAULT_TIMEOUT,
    base_url_from_env,
    api_key_from_env,
    api_secret_from_env,
)
from tradezero.http.async_http import AsyncHTTPClient
from tradezero.modules.accounts import AsyncAccountsModule
from tradezero.modules.trading import AsyncTradingModule
from tradezero.modules.positions import AsyncPositionsModule
from tradezero.modules.locates import AsyncLocatesModule


class AsyncTradeZeroClient:
    """Asynchronous entry-point for the TradeZero SDK.

    Designed to be used as an async context manager::

        async with AsyncTradeZeroClient(api_key="...", api_secret="...") as client:
            positions = await client.positions.get_positions("ACC123")

    Args:
        api_key: TradeZero API key ID.  Falls back to ``TZ_API_KEY``.
        api_secret: TradeZero API secret key.  Falls back to ``TZ_API_SECRET``.
        base_url: Override the default base URL.  Falls back to ``TZ_BASE_URL``
            or ``https://webapi.tradezero.com/v1/api``.
        timeout: Per-request timeout in seconds (default: 30).

    Attributes:
        accounts: :class:`~tradezero.modules.accounts.AsyncAccountsModule`
        trading: :class:`~tradezero.modules.trading.AsyncTradingModule`
        positions: :class:`~tradezero.modules.positions.AsyncPositionsModule`
        locates: :class:`~tradezero.modules.locates.AsyncLocatesModule`

    Raises:
        ValueError: If credentials are missing from both kwargs and env vars.
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

        self._http = AsyncHTTPClient(
            api_key=resolved_key,
            api_secret=resolved_secret,
            base_url=resolved_url,
            timeout=timeout,
        )

        # Domain modules
        self.accounts = AsyncAccountsModule(self._http)
        self.trading = AsyncTradingModule(self._http)
        self.positions = AsyncPositionsModule(self._http)
        self.locates = AsyncLocatesModule(self._http)

    async def aclose(self) -> None:
        """Release the underlying async HTTP connection pool."""
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncTradeZeroClient":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
