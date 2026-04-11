"""Shared utilities and header-building logic for HTTP clients."""

from __future__ import annotations

from typing import Any


def build_auth_headers(api_key: str, api_secret: str) -> dict[str, str]:
    """Return the authentication headers required by every TradeZero API request.

    Args:
        api_key: The ``TZ-API-KEY-ID`` value.
        api_secret: The ``TZ-API-SECRET-KEY`` value.

    Returns:
        A dictionary of HTTP headers to inject into every request.
    """
    return {
        "TZ-API-KEY-ID": api_key,
        "TZ-API-SECRET-KEY": api_secret,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def strip_none(params: dict[str, Any]) -> dict[str, Any]:
    """Remove keys whose value is ``None`` from a query-parameter dict.

    Args:
        params: Raw parameter mapping, possibly containing ``None`` values.

    Returns:
        A new dict with all ``None`` entries removed.
    """
    return {k: v for k, v in params.items() if v is not None}
