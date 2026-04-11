"""Asynchronous HTTP client built on ``httpx``."""

from __future__ import annotations

from typing import Any

import httpx

from tradezero.config import DEFAULT_TIMEOUT
from tradezero.exceptions import raise_for_status
from tradezero.http._base import build_auth_headers, strip_none
from tradezero.http._retry import sdk_retry


class AsyncHTTPClient:
    """Thin asynchronous wrapper around ``httpx.AsyncClient``.

    Injects authentication headers into every request and raises
    domain-specific SDK exceptions for non-2xx responses.

    Args:
        api_key: TradeZero API key ID.
        api_secret: TradeZero API secret key.
        base_url: Root URL for all API calls.
        timeout: Per-request timeout in seconds.
    """

    def __init__(
        self,
        *,
        api_key: str,
        api_secret: str,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            headers=build_auth_headers(api_key, api_secret),
            timeout=timeout,
        )

    # ── Public helpers ────────────────────────────────────────────────────────

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Perform an async GET request.

        Args:
            path: URL path relative to the base URL.
            params: Optional query parameters (``None`` values are stripped).

        Returns:
            Parsed JSON response body.
        """
        return await self._request("GET", path, params=params)

    async def post(self, path: str, *, json: Any = None) -> Any:
        """Perform an async POST request.

        Args:
            path: URL path relative to the base URL.
            json: JSON-serialisable request body.

        Returns:
            Parsed JSON response body.
        """
        return await self._request("POST", path, json=json)

    async def delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Perform an async DELETE request.

        Args:
            path: URL path relative to the base URL.
            params: Optional query parameters (``None`` values are stripped).
            data: Optional form-encoded body (sent as
                ``application/x-www-form-urlencoded``).

        Returns:
            Parsed JSON response body (may be ``None`` for 204 responses).
        """
        return await self._request("DELETE", path, params=params, data=data)

    async def aclose(self) -> None:
        """Close the underlying ``httpx.AsyncClient`` and free connections."""
        await self._client.aclose()

    # ── Context-manager support ───────────────────────────────────────────────

    async def __aenter__(self) -> AsyncHTTPClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()

    # ── Internal ──────────────────────────────────────────────────────────────

    @sdk_retry  # type: ignore[misc]
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Execute an async HTTP request with retry logic.

        Args:
            method: HTTP verb.
            path: URL path relative to the base URL.
            params: Query-string parameters.
            json: Request body to serialise as JSON.
            data: Form-encoded request body (overrides ``json`` if both set).

        Returns:
            Parsed JSON response, or ``None`` for empty bodies.

        Raises:
            TradeZeroAPIError: On any non-2xx response.
        """
        url = f"{self._base_url}/{path.lstrip('/')}"
        cleaned_params = strip_none(params) if params else None

        response = await self._client.request(
            method,
            url,
            params=cleaned_params,
            json=json,
            data=data,
        )

        if not response.is_success:
            raise_for_status(response.status_code, response.text, url)

        if response.status_code == 204 or not response.content:
            return None

        return response.json()
