from pathlib import Path

from src.domains.money.bot_parser import parse_bot_exchange_rates_html

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "bot_exchange_rates.html"


def test_parse_bot_exchange_rates_html_creates_three_metric_observations() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    observations = parse_bot_exchange_rates_html(
        html,
        source_url="https://www.bot.go.tz/exchangerate/excrates",
    )

    assert len(observations) == 3
    assert {observation.metric_slug for observation in observations} == {
        "fx_buy_rate",
        "fx_sell_rate",
        "fx_mean_rate",
    }
    assert {observation.detail.market_scope for observation in observations} == {
        "official_reference"
    }
    assert {observation.detail.instrument_code for observation in observations} == {
        "USD"
    }
