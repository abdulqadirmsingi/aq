from pathlib import Path

from src.domains.money.crdb_parser import parse_crdb_forex_html

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "crdb_forex.html"


def test_parse_crdb_forex_html_creates_buy_and_sell_observations() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    observations = parse_crdb_forex_html(
        html,
        source_url="https://crdbbank.co.tz/en/forex",
    )

    assert len(observations) == 2
    assert {observation.metric_slug for observation in observations} == {
        "fx_buy_rate",
        "fx_sell_rate",
    }
    assert {observation.detail.market_scope for observation in observations} == {
        "commercial_bank"
    }
    assert {observation.detail.channel for observation in observations} == {"counter"}
