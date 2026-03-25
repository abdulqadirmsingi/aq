from src.core.browser_fetcher import BrowserFetchUnavailableError
from src.domains.money.nmb_live_fetch import (
    NmbCloudflareChallengeError,
    fetch_nmb_daily_exchange_rates_html,
    is_cloudflare_challenge_html,
)


class _StubHttpClient:
    def __init__(self, html: str) -> None:
        self._html = html

    def get_text(self, url: str) -> str:
        return self._html


def test_cloudflare_detector_flags_challenge_page() -> None:
    html = (
        "<html><head><title>Just a moment...</title></head>"
        "<body>_cf_chl_opt</body></html>"
    )
    assert is_cloudflare_challenge_html(html) is True


def test_cloudflare_detector_ignores_normal_page() -> None:
    html = "<html><body><h2>Non Cash</h2><table></table></body></html>"
    assert is_cloudflare_challenge_html(html) is False


def test_fetch_nmb_html_raises_when_challenge_and_browser_and_mirror_unavailable(
    monkeypatch,
) -> None:
    challenge_html = (
        "<html><head><title>Just a moment...</title></head>"
        "<body>Enable JavaScript and cookies to continue</body></html>"
    )

    def _raise_browser_unavailable(*args, **kwargs):
        raise BrowserFetchUnavailableError("browser unavailable")

    monkeypatch.setattr(
        "src.domains.money.nmb_live_fetch.fetch_page_html",
        _raise_browser_unavailable,
    )
    monkeypatch.setattr(
        "src.domains.money.nmb_live_fetch._fetch_jina_markdown",
        lambda url: None,
    )

    try:
        fetch_nmb_daily_exchange_rates_html(
            "https://www.nmbbank.co.tz/treasury/foreign-exchange/nmb-daily-exchange-rates",
            http_client=_StubHttpClient(challenge_html),
        )
    except NmbCloudflareChallengeError as exc:
        assert "Cloudflare challenge" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected NmbCloudflareChallengeError")
