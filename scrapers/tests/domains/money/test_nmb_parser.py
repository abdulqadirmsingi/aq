from datetime import UTC, datetime
from pathlib import Path

from src.domains.money.nmb_parser import parse_nmb_daily_exchange_rates_html

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
