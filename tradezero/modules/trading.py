"""Trading module — synchronous and asynchronous order management."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from pydantic import ValidationError

from tradezero.enums import OrderSide, OrderType, SecurityType, TimeInForce
from tradezero.exceptions import APIValidationError
from tradezero.models.orders import CreateOrderRequest, Order, OrderResponse, TradeRecord

if TYPE_CHECKING:
    from tradezero.http.async_http import AsyncHTTPClient
    from tradezero.http.sync_http import SyncHTTPClient


class TradingModule:
    """Synchronous interface for the order management endpoints.

    Args:
        http: Configured synchronous HTTP client.
    """

    def __init__(self, http: "SyncHTTPClient") -> None:
        self._http = http

    def create_order(
        self,
        account_id: str,
        symbol: str,
        quantity: int,
        side: OrderSide | str,
        order_type: OrderType | str,
        time_in_force: TimeInForce | str,
        *,
        security_type: SecurityType | str = SecurityType.STOCK,
        limit_price: float | None = None,
        stop_price: float | None = None,
        client_order_id: str | None = None,
        route: str | None = None,
    ) -> OrderResponse:
        """Submit a new trade order.

        Args:
            account_id: Target account identifier.
            symbol: Ticker symbol (e.g., ``"AAPL"``).
            quantity: Number of shares.
            side: ``"Buy"`` or ``"Sell"`` (or :class:`~tradezero.enums.OrderSide`).
            order_type: Execution style (e.g., ``"Limit"``).
            time_in_force: Duration instruction (e.g., ``"Day"``).
            security_type: ``"Stock"`` or ``"Option"`` (default: ``"Stock"``).
            limit_price: Required for ``Limit`` and ``StopLimit`` orders.
            stop_price: Required for ``Stop`` and ``StopLimit`` orders.
            client_order_id: Optional caller-supplied identifier (max 375 chars).
            route: Optional routing destination (e.g., ``"SMART"``).

        Returns:
            An :class:`~tradezero.models.orders.OrderResponse` with fill status.

        Raises:
            APIValidationError: If the request payload fails validation.
        """
        try:
            payload = CreateOrderRequest(
                symbol=symbol,
                order_quantity=quantity,
                side=OrderSide(side),
                order_type=OrderType(order_type),
                time_in_force=TimeInForce(time_in_force),
                security_type=SecurityType(security_type),
                limit_price=limit_price,
                stop_price=stop_price,
                client_order_id=client_order_id,
                route=route,
            )
        except (ValidationError, ValueError) as e:
            raise APIValidationError(str(e)) from e

        data = self._http.post(
            f"/accounts/{account_id}/order",
            json=json.loads(payload.model_dump_json(by_alias=True, exclude_none=True)),
        )
        return OrderResponse.model_validate(data)

    def list_orders(self, account_id: str) -> list[Order]:
        """Return all orders (pending, filled, canceled) for today.

        Args:
            account_id: Account identifier to query.

        Returns:
            A list of :class:`~tradezero.models.orders.Order` records.
        """
        data = self._http.get(f"/accounts/{account_id}/orders")
        if isinstance(data, dict):
            data = data.get("orders", [])
        return [Order.model_validate(item) for item in data]

    def list_historical_orders(
        self,
        account_id: str,
        start_date: str,
    ) -> list[TradeRecord]:
        """Return executed trade records starting from a calendar date.

        Retrieves up to one week of historical orders. Only available for
        live production accounts — paper trading accounts are not supported.

        Args:
            account_id: Account identifier to query.
            start_date: Start of the date range in ``YYYY-MM-DD`` format.

        Returns:
            A list of :class:`~tradezero.models.orders.TradeRecord` objects.

        Raises:
            APIValidationError: If the response cannot be parsed.
        """
        path = f"/accounts/{account_id}/orders/start-date/{start_date}"
        data = self._http.get(path)
        if isinstance(data, dict):
            data = data.get("trades", data.get("orders", []))
        try:
            return [TradeRecord.model_validate(item) for item in data]
        except ValidationError as e:
            raise APIValidationError(str(e)) from e

    def cancel_order(self, account_id: str, client_order_id: str) -> None:
        """Cancel a specific open order by its client order ID.

        The order must be in ``new`` or ``partially_filled`` status.

        Args:
            account_id: Account that owns the order.
            client_order_id: Identifier of the order to cancel.
        """
        self._http.delete(f"/accounts/{account_id}/orders/{client_order_id}")

    def cancel_all_orders(
        self,
        account_id: str,
        *,
        symbol: str | None = None,
    ) -> dict | None:
        """Cancel all open orders for a specific account.

        Args:
            account_id: The account for which to cancel all open orders.
            symbol: Optional ticker symbol to restrict cancellations to.

        Returns:
            API confirmation dict, or ``None`` if no body is returned.
        """
        params = {"symbol": symbol} if symbol else None
        return self._http.delete(
            "/accounts/orders",
            params=params,
            data={"account": account_id},
        )

    def is_easy_to_borrow(self, account_id: str, symbol: str) -> bool:
        """Check whether a symbol is easy to borrow for short selling.

        Args:
            account_id: The account identifier.
            symbol: Ticker symbol to check (e.g., ``"AAPL"``).

        Returns:
            ``True`` if the symbol is easy to borrow, ``False`` otherwise.
        """
        data = self._http.get(
            f"/accounts/{account_id}/is-easy-to-borrow/symbol/{symbol}"
        )
        if isinstance(data, dict):
            return bool(data.get("isEasyToBorrow", False))
        return bool(data)

    def get_routes(self, account_id: str) -> list[dict]:
        """Retrieve all available trading routes for an account.

        Args:
            account_id: The account identifier.

        Returns:
            A list of route dictionaries (structure depends on the API response).
        """
        data = self._http.get(f"/accounts/{account_id}/routes")
        if isinstance(data, dict):
            return data.get("routes", [])
        return data or []


class AsyncTradingModule:
    """Asynchronous interface for the order management endpoints.

    Args:
        http: Configured asynchronous HTTP client.
    """

    def __init__(self, http: "AsyncHTTPClient") -> None:
        self._http = http

    async def create_order(
        self,
        account_id: str,
        symbol: str,
        quantity: int,
        side: OrderSide | str,
        order_type: OrderType | str,
        time_in_force: TimeInForce | str,
        *,
        security_type: SecurityType | str = SecurityType.STOCK,
        limit_price: float | None = None,
        stop_price: float | None = None,
        client_order_id: str | None = None,
        route: str | None = None,
    ) -> OrderResponse:
        """Async version of :meth:`TradingModule.create_order`."""
        try:
            payload = CreateOrderRequest(
                symbol=symbol,
                order_quantity=quantity,
                side=OrderSide(side),
                order_type=OrderType(order_type),
                time_in_force=TimeInForce(time_in_force),
                security_type=SecurityType(security_type),
                limit_price=limit_price,
                stop_price=stop_price,
                client_order_id=client_order_id,
                route=route,
            )
        except (ValidationError, ValueError) as e:
            raise APIValidationError(str(e)) from e

        data = await self._http.post(
            f"/accounts/{account_id}/order",
            json=json.loads(payload.model_dump_json(by_alias=True, exclude_none=True)),
        )
        return OrderResponse.model_validate(data)

    async def list_orders(self, account_id: str) -> list[Order]:
        """Async version of :meth:`TradingModule.list_orders`."""
        data = await self._http.get(f"/accounts/{account_id}/orders")
        if isinstance(data, dict):
            data = data.get("orders", [])
        return [Order.model_validate(item) for item in data]

    async def list_historical_orders(
        self,
        account_id: str,
        start_date: str,
    ) -> list[TradeRecord]:
        """Async version of :meth:`TradingModule.list_historical_orders`."""
        path = f"/accounts/{account_id}/orders/start-date/{start_date}"
        data = await self._http.get(path)
        if isinstance(data, dict):
            data = data.get("trades", data.get("orders", []))
        try:
            return [TradeRecord.model_validate(item) for item in data]
        except ValidationError as e:
            raise APIValidationError(str(e)) from e

    async def cancel_order(self, account_id: str, client_order_id: str) -> None:
        """Async version of :meth:`TradingModule.cancel_order`."""
        await self._http.delete(f"/accounts/{account_id}/orders/{client_order_id}")

    async def cancel_all_orders(
        self,
        account_id: str,
        *,
        symbol: str | None = None,
    ) -> dict | None:
        """Async version of :meth:`TradingModule.cancel_all_orders`."""
        params = {"symbol": symbol} if symbol else None
        return await self._http.delete(
            "/accounts/orders",
            params=params,
            data={"account": account_id},
        )

    async def is_easy_to_borrow(self, account_id: str, symbol: str) -> bool:
        """Async version of :meth:`TradingModule.is_easy_to_borrow`."""
        data = await self._http.get(
            f"/accounts/{account_id}/is-easy-to-borrow/symbol/{symbol}"
        )
        if isinstance(data, dict):
            return bool(data.get("isEasyToBorrow", False))
        return bool(data)

    async def get_routes(self, account_id: str) -> list[dict]:
        """Async version of :meth:`TradingModule.get_routes`."""
        data = await self._http.get(f"/accounts/{account_id}/routes")
        if isinstance(data, dict):
            return data.get("routes", [])
        return data or []

