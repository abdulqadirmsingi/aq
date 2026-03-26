"""Live fetch helpers for NMB, including Cloudflare/browser fallback."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from src.core.browser_fetcher import (
    BrowserFetchUnavailableError,
    fetch_page_html,
)
from src.core.http_client import ScraperHttpClient


class NmbCloudflareChallengeError(RuntimeError):
    """Raised when NMB returns a Cloudflare challenge instead of rate tables."""


@dataclass(frozen=True)
class NmbFetchResult:
    content: str
    source_url: str
    used_browser_fallback: bool
    content_format: str


def is_cloudflare_challenge_html(html: str) -> bool:
    lowered = html.lower()
    return (
        "just a moment..." in lowered
        or "enable javascript and cookies to continue" in lowered
        or "_cf_chl_opt" in lowered
    )


def has_nmb_rate_content(content: str) -> bool:
    lowered = content.lower()
    return (
        "forex market: non cash exchange rates" in lowered
        or "cash and non-cash rates" in lowered
        or "50 - 500 buy" in lowered
    )


def fetch_nmb_daily_exchange_rates_html(
    url: str,
    *,
    http_client: ScraperHttpClient,
) -> NmbFetchResult:
    try:
        html = http_client.get_text(url)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code != 403:
            raise
        html = ""
    else:
        if not is_cloudflare_challenge_html(html) and has_nmb_rate_content(html):
            return NmbFetchResult(
                content=html,
                source_url=url,
                used_browser_fallback=False,
                content_format="html",
            )

    try:
        browser_result = fetch_page_html(url)
    except BrowserFetchUnavailableError as exc:
        markdown = _fetch_jina_markdown(url)
        if markdown is not None:
            return NmbFetchResult(
                content=markdown,
                source_url=url,
                used_browser_fallback=False,
                content_format="markdown",
            )
        raise NmbCloudflareChallengeError(
            "NMB returned a Cloudflare challenge and Playwright fallback is not "
            "available. Install Playwright in scrapers and run "
            "`poetry run playwright install chromium`."
        ) from exc
    except Exception as exc:
        markdown = _fetch_jina_markdown(url)
        if markdown is not None:
            return NmbFetchResult(
                content=markdown,
                source_url=url,
                used_browser_fallback=False,
                content_format="markdown",
            )
        raise NmbCloudflareChallengeError(
            "NMB browser fallback failed before the mirror fallback could recover."
        ) from exc

    if is_cloudflare_challenge_html(browser_result.html):
        markdown = _fetch_jina_markdown(url)
        if markdown is not None:
            return NmbFetchResult(
                content=markdown,
                source_url=url,
                used_browser_fallback=False,
                content_format="markdown",
            )
        raise NmbCloudflareChallengeError(
            "NMB still returned a Cloudflare challenge after browser fallback."
        )

    return NmbFetchResult(
        content=browser_result.html,
        source_url=browser_result.final_url,
        used_browser_fallback=True,
        content_format="html",
    )


def _fetch_jina_markdown(url: str) -> str | None:
    mirror_url = f"https://r.jina.ai/http://{url}"
    response = httpx.get(mirror_url, timeout=60, follow_redirects=True)
    response.raise_for_status()
    text = response.text
    if not has_nmb_rate_content(text):
        return None
    return text
