"""Locates module — synchronous and asynchronous variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tradezero.models.locates import (
    LocateAcceptRequest,
    LocateHistoryItem,
    LocateInventoryItem,
    LocateQuoteRequest,
    LocateSellRequest,
)
from tradezero.enums import LocateTypeStr

if TYPE_CHECKING:
    from tradezero.http.sync_http import SyncHTTPClient
    from tradezero.http.async_http import AsyncHTTPClient


class LocatesModule:
    """Synchronous interface for the locate management endpoints.

    Args:
        http: Configured synchronous HTTP client.
    """

    def __init__(self, http: "SyncHTTPClient") -> None:
        self._http = http

    def request_quote(
        self,
        account: str,
        symbol: str,
        quantity: int,
        quote_req_id: str,
    ) -> dict:
        """Submit a locate quote request.

        Args:
            account: Account requesting the locate.
            symbol: Ticker symbol to locate.
            quantity: Number of shares to locate.
            quote_req_id: Unique client-generated request identifier.

        Returns:
            Raw API response dict.
        """
        payload = LocateQuoteRequest(
            account=account,
            symbol=symbol,
            quantity=quantity,
            quoteReqID=quote_req_id,
        )
        return self._http.post(
            "/accounts/locates/quote",
            json=payload.model_dump(by_alias=True),
        )

    def get_inventory(self, account_id: str) -> list[LocateInventoryItem]:
        """Return active locate inventory available for the day.

        Args:
            account_id: Account identifier.

        Returns:
            A list of :class:`~tradezero.models.locates.LocateInventoryItem` entries.
        """
        data = self._http.get(f"/accounts/{account_id}/locates/inventory")
        if isinstance(data, dict):
            data = data.get("locateInventory", [])
        return [LocateInventoryItem.model_validate(item) for item in data]

    def get_history(self, account_id: str) -> list[LocateHistoryItem]:
        """Poll locate request history to check quote status.

        Poll for ``locate_status == LocateStatus.OFFERED`` (65) before
        calling :meth:`accept_quote`.

        Args:
            account_id: Account identifier.

        Returns:
            A list of :class:`~tradezero.models.locates.LocateHistoryItem` records.
        """
        data = self._http.get(f"/accounts/{account_id}/locates/history")
        if isinstance(data, dict):
            data = data.get("locateHistory", [])
        return [LocateHistoryItem.model_validate(item) for item in data]

    def accept_quote(self, account_id: str, quote_req_id: str) -> dict:
        """Accept an offered locate quote.

        Args:
            account_id: Account that owns the locate.
            quote_req_id: Identifier from the original quote request.

        Returns:
            Raw API response dict.
        """
        payload = LocateAcceptRequest(accountId=account_id, quoteReqID=quote_req_id)
        return self._http.post(
            "/accounts/locates/accept",
            json=payload.model_dump(by_alias=True),
        )

    def sell_locate(
        self,
        account: str,
        symbol: str,
        quote_req_id: str,
        quantity: int,
        locate_type: LocateTypeStr | str,
    ) -> dict:
        """Sell (credit back) locate inventory.

        Args:
            account: Account ID.
            symbol: Ticker symbol.
            quote_req_id: New unique identifier for this sell action.
            quantity: Shares to sell back (must be ≤ available).
            locate_type: Locate type string (e.g., ``"Locate"``).

        Returns:
            Raw API response dict.
        """
        payload = LocateSellRequest(
            account=account,
            symbol=symbol,
            quoteReqID=quote_req_id,
            quantity=quantity,
            locateType=LocateTypeStr(locate_type),
        )
        return self._http.post(
            "/accounts/locates/sell",
            json=payload.model_dump(by_alias=True),
        )

    def cancel_locate(self, account_id: str, quote_req_id: str) -> None:
        """Cancel an offered locate quote or a pending sell request.

        Args:
            account_id: Account identifier.
            quote_req_id: Identifier of the quote to cancel.
        """
        self._http.delete(
            f"/accounts/locates/cancel/accounts/{account_id}/quoteReqID/{quote_req_id}"
        )


class AsyncLocatesModule:
    """Asynchronous interface for the locate management endpoints.

    Args:
        http: Configured asynchronous HTTP client.
    """

    def __init__(self, http: "AsyncHTTPClient") -> None:
        self._http = http

    async def request_quote(
        self,
        account: str,
        symbol: str,
        quantity: int,
        quote_req_id: str,
    ) -> dict:
        """Async version of :meth:`LocatesModule.request_quote`."""
        payload = LocateQuoteRequest(
            account=account,
            symbol=symbol,
            quantity=quantity,
            quoteReqID=quote_req_id,
        )
        return await self._http.post(
            "/accounts/locates/quote",
            json=payload.model_dump(by_alias=True),
        )

    async def get_inventory(self, account_id: str) -> list[LocateInventoryItem]:
        """Async version of :meth:`LocatesModule.get_inventory`."""
        data = await self._http.get(f"/accounts/{account_id}/locates/inventory")
        if isinstance(data, dict):
            data = data.get("locateInventory", [])
        return [LocateInventoryItem.model_validate(item) for item in data]

    async def get_history(self, account_id: str) -> list[LocateHistoryItem]:
        """Async version of :meth:`LocatesModule.get_history`."""
        data = await self._http.get(f"/accounts/{account_id}/locates/history")
        if isinstance(data, dict):
            data = data.get("locateHistory", [])
        return [LocateHistoryItem.model_validate(item) for item in data]

    async def accept_quote(self, account_id: str, quote_req_id: str) -> dict:
        """Async version of :meth:`LocatesModule.accept_quote`."""
        payload = LocateAcceptRequest(accountId=account_id, quoteReqID=quote_req_id)
        return await self._http.post(
            "/accounts/locates/accept",
            json=payload.model_dump(by_alias=True),
        )

    async def sell_locate(
        self,
        account: str,
        symbol: str,
        quote_req_id: str,
        quantity: int,
        locate_type: LocateTypeStr | str,
    ) -> dict:
        """Async version of :meth:`LocatesModule.sell_locate`."""
        payload = LocateSellRequest(
            account=account,
            symbol=symbol,
            quoteReqID=quote_req_id,
            quantity=quantity,
            locateType=LocateTypeStr(locate_type),
        )
        return await self._http.post(
            "/accounts/locates/sell",
            json=payload.model_dump(by_alias=True),
        )

    async def cancel_locate(self, account_id: str, quote_req_id: str) -> None:
        """Async version of :meth:`LocatesModule.cancel_locate`."""
        await self._http.delete(
            f"/accounts/locates/cancel/accounts/{account_id}/quoteReqID/{quote_req_id}"
        )
