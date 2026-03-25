"""Optional browser-backed fetch helpers for anti-bot protected sources."""

from __future__ import annotations

from dataclasses import dataclass


class BrowserFetchUnavailableError(RuntimeError):
    """Raised when browser automation is requested but not available."""


@dataclass(frozen=True)
class BrowserFetchResult:
    html: str
    final_url: str


def fetch_page_html(
    url: str,
    *,
    timeout_ms: int = 30_000,
    wait_until: str = "domcontentloaded",
) -> BrowserFetchResult:
    """Fetch a page with Playwright Chromium for JS / anti-bot protected pages."""

    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional install
        raise BrowserFetchUnavailableError(
            "Playwright is not installed. Install it in scrapers and run "
            "`poetry run playwright install chromium`."
        ) from exc

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1440, "height": 1200},
                locale="en-US",
            )
            page = context.new_page()
            response = page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            if response is not None and response.status >= 400:
                raise RuntimeError(
                    f"Browser fetch failed with HTTP {response.status} for {url}"
                )
            page.wait_for_timeout(3_000)
            return BrowserFetchResult(html=page.content(), final_url=page.url)
        finally:
            browser.close()
