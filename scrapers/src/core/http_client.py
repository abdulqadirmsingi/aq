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

    @http_retry()
    def get_json(self, url: str) -> object:
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()

    @http_retry()
    def get_bytes_bounded(self, url: str, max_bytes: int) -> bytes:
        """Stream response body; raises if ``max_bytes`` is exceeded."""
        with self._client.stream("GET", url) as response:
            response.raise_for_status()
            cl = response.headers.get("content-length")
            if cl is not None:
                try:
                    declared = int(cl)
                except ValueError:
                    declared = None
                if declared is not None and declared > max_bytes:
                    msg = f"Content-Length {cl} exceeds cap {max_bytes}"
                    raise ValueError(msg)
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > max_bytes:
                    msg = f"Download exceeded max_bytes={max_bytes}"
                    raise ValueError(msg)
                chunks.append(chunk)
            return b"".join(chunks)
