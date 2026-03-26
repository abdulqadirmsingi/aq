from app.modules.money.constants import EXCHANGE_RATE_METRICS, EXCHANGE_RATE_SOURCES
from app.modules.money.models.exchange_rate import ExchangeRateDetail


def test_exchange_rate_source_slugs_are_unique() -> None:
    slugs = [source.slug for source in EXCHANGE_RATE_SOURCES]
    assert slugs == [
        "bot_exchange_rates",
        "crdb_forex",
        "nmb_daily_exchange_rates",
    ]
    assert len(slugs) == len(set(slugs))


def test_exchange_rate_metric_slugs_are_unique() -> None:
    slugs = [metric.slug for metric in EXCHANGE_RATE_METRICS]
    assert slugs == ["fx_buy_rate", "fx_sell_rate", "fx_mean_rate"]
    assert len(slugs) == len(set(slugs))


def test_exchange_rate_detail_supports_richer_dimensions() -> None:
    table = ExchangeRateDetail.__table__

    assert table.c.instrument_code.type.length == 16
    assert table.c.quote_code.type.length == 16
    assert table.c.instrument_type.server_default.arg == "currency"
    assert not table.c.rate_kind.nullable
    assert not table.c.market_scope.nullable

    index_names = {index.name for index in table.indexes}
    assert "ix_exchange_rate_details_lookup" in index_names
    assert "ix_exchange_rate_details_market_channel" in index_names
