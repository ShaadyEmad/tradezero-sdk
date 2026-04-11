"""Tenacity-based retry configuration shared by both HTTP clients."""

from __future__ import annotations

import logging

import httpx
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from tradezero.config import DEFAULT_MAX_RETRIES, DEFAULT_RETRY_WAIT_SECONDS
from tradezero.exceptions import RateLimitError, ServerError

logger = logging.getLogger(__name__)


def _is_retryable(exc: BaseException) -> bool:
    """Return ``True`` for errors that warrant an automatic retry.

    Retries are attempted for:

    - ``httpx.TransportError`` (network-level failures, e.g. connection reset)
    - :class:`~tradezero.exceptions.RateLimitError` (HTTP 429 Too Many Requests)
    - :class:`~tradezero.exceptions.ServerError` (HTTP 5xx server-side errors)

    Args:
        exc: The exception raised by the HTTP call.

    Returns:
        ``True`` if the request should be retried.
    """
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, RateLimitError | ServerError):
        return True
    return False


def _log_retry(retry_state: RetryCallState) -> None:
    """Log each retry attempt at WARNING level.

    Args:
        retry_state: Tenacity state object for the current retry cycle.
    """
    logger.warning(
        "TradeZero SDK — retry attempt %d/%d after error: %s",
        retry_state.attempt_number,
        DEFAULT_MAX_RETRIES,
        retry_state.outcome.exception() if retry_state.outcome else "unknown",
    )


#: Pre-built ``@retry`` decorator used by both sync and async clients.
sdk_retry = retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
    wait=wait_exponential(
        multiplier=DEFAULT_RETRY_WAIT_SECONDS,
        min=DEFAULT_RETRY_WAIT_SECONDS,
        max=60,
    ),
    before_sleep=_log_retry,
    reraise=True,
)
