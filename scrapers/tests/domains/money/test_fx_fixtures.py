from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_exchange_rate_html_fixtures_exist() -> None:
    fixture_names = {
        "bot_exchange_rates.html",
        "crdb_forex.html",
        "nmb_daily_exchange_rates.html",
    }
    existing = {path.name for path in FIXTURES_DIR.iterdir() if path.is_file()}
    assert fixture_names.issubset(existing)


def test_bot_fixture_contains_table_headers() -> None:
    html = (FIXTURES_DIR / "bot_exchange_rates.html").read_text(encoding="utf-8")
    assert "Transaction Date" in html
    assert "USD" in html
