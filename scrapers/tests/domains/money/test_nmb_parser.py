from datetime import UTC, datetime
from pathlib import Path

from src.domains.money.nmb_parser import (
    parse_nmb_daily_exchange_rates_html,
    parse_nmb_daily_exchange_rates_markdown,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "nmb_daily_exchange_rates.html"
)


def test_parse_nmb_daily_exchange_rates_html_preserves_channels_and_note_bands(
) -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    observations = parse_nmb_daily_exchange_rates_html(
        html,
        source_url="https://www.nmbbank.co.tz/treasury/foreign-exchange/nmb-daily-exchange-rates",
        observed_at=datetime(2026, 3, 25, 0, 0, tzinfo=UTC),
    )

    assert len(observations) == 6
    assert {observation.detail.channel for observation in observations} == {
        "non_cash",
        "cash",
    }
    assert {observation.detail.cash_note_band for observation in observations} == {
        None,
        "notes_50_500",
        "notes_1_20",
    }


def test_parse_nmb_daily_exchange_rates_markdown_preserves_channels_and_note_bands(
) -> None:
    markdown = """
## Cash and Non-Cash Rates

FOREX MARKET: NON CASH EXCHANGE RATES

| # | Currency | CODE | Buy | Sell |
| --- | --- | --- | --- | --- |
| 1 | US Dollars | USD | 2,535 | 2,615 |
| 2 | Euro | EUR | 2,845 | 3,119 |

FOREX MARKET: CASH EXCHANGE RATES

| Currency | CODE | 50, 100, 200, & 500 | 1, 2, 5, 10, & 20 |
| --- | --- | --- | --- |
|  |  | 50 - 500 Buy | 50 - 500 Sell | 1 - 20 Buy | 1 - 20 Sell |
| US Dollars | USD | 2,535 | 2,615 | 2,535 | 2,615 |
| Euro | EUR | 2,845 | 3,119 | 2,845 | 3,119 |
"""

    observations = parse_nmb_daily_exchange_rates_markdown(
        markdown,
        source_url="https://www.nmbbank.co.tz/treasury/foreign-exchange/nmb-daily-exchange-rates",
        observed_at=datetime(2026, 3, 25, 0, 0, tzinfo=UTC),
    )

    assert len(observations) == 12
    assert {observation.detail.channel for observation in observations} == {
        "non_cash",
        "cash",
    }
    assert {observation.detail.cash_note_band for observation in observations} == {
        None,
        "notes_50_500",
        "notes_1_20",
    }
