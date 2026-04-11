"""Accounts module — synchronous and asynchronous variants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tradezero.models.accounts import Account, AccountPnL

if TYPE_CHECKING:
    from tradezero.http.async_http import AsyncHTTPClient
    from tradezero.http.sync_http import SyncHTTPClient


class AccountsModule:
    """Synchronous interface for the ``/accounts`` and ``/account`` endpoints.

    Args:
        http: Configured synchronous HTTP client.
    """

    def __init__(self, http: "SyncHTTPClient") -> None:
        self._http = http

    def list_accounts(self) -> list[Account]:
        """Retrieve all trading accounts associated with the API credentials.

        Returns:
            A list of :class:`~tradezero.models.accounts.Account` objects.
        """
        data = self._http.get("/accounts")
        if isinstance(data, dict):
            data = data.get("accounts", [])
        return [Account.model_validate(item) for item in data]

    def get_account_details(self, account_id: str) -> Account:
        """Retrieve full account details for one account.

        The ``GET /account/:id`` endpoint returns the same field structure
        as ``GET /accounts``, so this method returns an
        :class:`~tradezero.models.accounts.Account` object.

        Args:
            account_id: The unique account identifier.

        Returns:
            An :class:`~tradezero.models.accounts.Account` instance.
        """
        data = self._http.get(f"/account/{account_id}")
        return Account.model_validate(data)

    def get_account_pnl(self, account_id: str) -> AccountPnL:
        """Retrieve settlement cash and daily P&L figures for one account.

        Args:
            account_id: The unique account identifier.

        Returns:
            An :class:`~tradezero.models.accounts.AccountPnL` instance.
        """
        data = self._http.get(f"/accounts/{account_id}/pnl")
        return AccountPnL.model_validate(data)


class AsyncAccountsModule:
    """Asynchronous interface for the ``/accounts`` and ``/account`` endpoints.

    Args:
        http: Configured asynchronous HTTP client.
    """

    def __init__(self, http: "AsyncHTTPClient") -> None:
        self._http = http

    async def list_accounts(self) -> list[Account]:
        """Async version of :meth:`AccountsModule.list_accounts`."""
        data = await self._http.get("/accounts")
        if isinstance(data, dict):
            data = data.get("accounts", [])
        return [Account.model_validate(item) for item in data]

    async def get_account_details(self, account_id: str) -> Account:
        """Async version of :meth:`AccountsModule.get_account_details`."""
        data = await self._http.get(f"/account/{account_id}")
        return Account.model_validate(data)

    async def get_account_pnl(self, account_id: str) -> AccountPnL:
        """Async version of :meth:`AccountsModule.get_account_pnl`."""
        data = await self._http.get(f"/accounts/{account_id}/pnl")
        return AccountPnL.model_validate(data)
