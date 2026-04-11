"""Positions module — synchronous and asynchronous variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tradezero.models.positions import Position

if TYPE_CHECKING:
    from tradezero.http.async_http import AsyncHTTPClient
    from tradezero.http.sync_http import SyncHTTPClient


class PositionsModule:
    """Synchronous interface for the ``/positions`` endpoint.

    Args:
        http: Configured synchronous HTTP client.
    """

    def __init__(self, http: SyncHTTPClient) -> None:
        self._http = http

    def get_positions(self, account_id: str) -> list[Position]:
        """Retrieve all open positions for an account.

        Each :class:`~tradezero.models.positions.Position` exposes an
        ``unrealized_pnl`` computed property.

        Args:
            account_id: Account identifier to query.

        Returns:
            A list of open :class:`~tradezero.models.positions.Position` objects.
        """
        data = self._http.get(f"/accounts/{account_id}/positions")
        
        # Check if the API wrapped the list in a dictionary key
        if isinstance(data, dict):
            # Extract the actual list of positions (fallback to empty list if missing)
            data = data.get("positions", [])
            
        return [Position.model_validate(item) for item in data]


class AsyncPositionsModule:
    """Asynchronous interface for the ``/positions`` endpoint.

    Args:
        http: Configured asynchronous HTTP client.
    """

    def __init__(self, http: AsyncHTTPClient) -> None:
        self._http = http

    async def get_positions(self, account_id: str) -> list[Position]:
        """Async version of :meth:`PositionsModule.get_positions`."""
        data = await self._http.get(f"/accounts/{account_id}/positions")
        
        # Check if the API wrapped the list in a dictionary key
        if isinstance(data, dict):
            data = data.get("positions", [])
            
        return [Position.model_validate(item) for item in data]

