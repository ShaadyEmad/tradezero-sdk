"""Custom exception hierarchy for the TradeZero SDK."""

from __future__ import annotations

from typing import Any


class TradeZeroSDKError(Exception):
    """Base exception for all SDK errors."""


class TradeZeroAPIError(TradeZeroSDKError):
    """Raised when the TradeZero API returns a non-2xx response.

    Attributes:
        status_code: HTTP status code returned by the API.
        response_body: Raw response body text.
        detail: Human-readable error detail extracted from the response.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"{type(self).__name__}(status_code={self.status_code!r}, "
            f"message={str(self)!r})"
        )


class AuthenticationError(TradeZeroAPIError):
    """Raised on 401 Unauthorized responses."""


class ForbiddenError(TradeZeroAPIError):
    """Raised on 403 Forbidden responses."""


class NotFoundError(TradeZeroAPIError):
    """Raised on 404 Not Found responses."""


class RateLimitError(TradeZeroAPIError):
    """Raised on 429 Too Many Requests responses."""


class APIValidationError(TradeZeroAPIError):
    """Raised on 422 Unprocessable Entity (invalid request payload)."""


class InsufficientFundsError(TradeZeroAPIError):
    """Raised when the account has insufficient buying power."""


class ServerError(TradeZeroAPIError):
    """Raised on 5xx server-side errors."""


# ── Status-code → exception mapping ──────────────────────────────────────────

_STATUS_MAP: dict[int, type[TradeZeroAPIError]] = {
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    422: APIValidationError,
    429: RateLimitError,
}


def raise_for_status(status_code: int, body: str, url: str) -> None:
    """Map an HTTP status code to the appropriate SDK exception and raise it.

    Args:
        status_code: HTTP status code from the API response.
        body: Raw response body text for debugging.
        url: Request URL for context in the error message.

    Raises:
        TradeZeroAPIError: Always raised with the most specific subclass available.
    """
    exc_cls = _STATUS_MAP.get(status_code)
    if exc_cls is None:
        exc_cls = ServerError if status_code >= 500 else TradeZeroAPIError

    # Attempt to surface a friendly message from the body
    try:
        import json
        data: Any = json.loads(body)
        detail = data.get("message") or data.get("detail") or data.get("error") or body
    except Exception:
        detail = body or "No detail provided."

    raise exc_cls(
        f"[{status_code}] {url} — {detail}",
        status_code=status_code,
        response_body=body,
    )
