"""SDK configuration and constants."""

from __future__ import annotations

import os

DEFAULT_BASE_URL: str = "https://webapi.tradezero.com/v1/api"

#: Maximum number of retry attempts for transient errors.
DEFAULT_MAX_RETRIES: int = 3

#: Seconds to wait before the first retry.
DEFAULT_RETRY_WAIT_SECONDS: float = 1.0

#: HTTP timeout in seconds.
DEFAULT_TIMEOUT: float = 30.0


def base_url_from_env() -> str:
    """Return the base URL, preferring the ``TZ_BASE_URL`` environment variable."""
    return os.environ.get("TZ_BASE_URL", DEFAULT_BASE_URL)


def api_key_from_env() -> str | None:
    """Return the API key from ``TZ_API_KEY`` or ``None``."""
    return os.environ.get("TZ_API_KEY")


def api_secret_from_env() -> str | None:
    """Return the API secret from ``TZ_API_SECRET`` or ``None``."""
    return os.environ.get("TZ_API_SECRET")
