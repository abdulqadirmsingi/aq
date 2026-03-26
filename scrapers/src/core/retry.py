"""Retry/backoff for resilient HTTP calls (tenacity)."""

from collections.abc import Callable
from typing import ParamSpec, TypeVar

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

P = ParamSpec("P")
R = TypeVar("R")


def _transient_http_failure(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return should_retry_http_error(exc)
    return False


def http_retry() -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry transient HTTP/network failures with bounded exponential backoff."""

    return retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential_jitter(initial=1, max=20),
        retry=retry_if_exception(_transient_http_failure),
    )


def should_retry_http_error(exc: BaseException) -> bool:
    """Treat 5xx and 429 as retryable when using manual retry loops."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500 or exc.response.status_code == 429
    return isinstance(exc, (httpx.TimeoutException, httpx.TransportError))
