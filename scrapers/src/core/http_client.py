"""Shared HTTP client for scrapers (httpx, timeouts, optional test transport)."""

from __future__ import annotations

import httpx

from src.core.config import ScraperSettings, load_settings
from src.core.retry import http_retry


class ScraperHttpClient:
    """Synchronous httpx client — suitable for Celery workers."""

    def __init__(
        self,
        settings: ScraperSettings | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings or load_settings()
        self._client = httpx.Client(
            timeout=self._settings.http_timeout_seconds,
            headers={"User-Agent": self._settings.user_agent},
            transport=transport,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> ScraperHttpClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    @http_retry()
    def get_text(self, url: str) -> str:
        response = self._client.get(url)
        response.raise_for_status()
        return response.text
