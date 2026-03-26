from datetime import UTC, date, datetime
from decimal import Decimal

from app.modules.money.repositories.exchange_rate_repository import (
    BotExchangeRateMonthRecord,
    BotExchangeRateRecord,
    ExchangeRateComparisonRecord,
)
from app.modules.money.services.exchange_rate_service import ExchangeRateService


class _FakeExchangeRateRepository:
    def __init__(self) -> None:
        self._comparison_rows = [
            ExchangeRateComparisonRecord(
                source_slug="bot_exchange_rates",
                source_name="Bank of Tanzania Exchange Rates",
                snapshot_date=date(2026, 3, 25),
                instrument_code="USD",
                instrument_name="USD",
                quote_code="TZS",
                buy_rate=Decimal("2557.8218"),
                sell_rate=Decimal("2583.4000"),
                mean_rate=Decimal("2570.6109"),
                source_effective_date=date(2026, 3, 25),
                source_last_updated_at=None,
                market_scope="official_reference",
                channel=None,
                cash_note_band=None,
                created_at=datetime(2026, 3, 25, 0, 0, tzinfo=UTC),
            ),
            ExchangeRateComparisonRecord(
                source_slug="crdb_forex",
                source_name="CRDB Forex Rates",
                snapshot_date=date(2026, 3, 25),
                instrument_code="USD",
                instrument_name="US DOLLAR",
                quote_code="TZS",
                buy_rate=Decimal("2535"),
                sell_rate=Decimal("2615"),
                mean_rate=None,
                source_effective_date=date(2026, 3, 25),
                source_last_updated_at=datetime(2026, 3, 25, 23, 17, tzinfo=UTC),
                market_scope="commercial_bank",
                channel="counter",
                cash_note_band=None,
                created_at=datetime(2026, 3, 25, 23, 17, tzinfo=UTC),
            ),
            ExchangeRateComparisonRecord(
                source_slug="nmb_daily_exchange_rates",
                source_name="NMB Daily Exchange Rates",
                snapshot_date=date(2026, 3, 25),
                instrument_code="USD",
                instrument_name="US Dollar",
                quote_code="TZS",
                buy_rate=Decimal("2535"),
                sell_rate=Decimal("2615"),
                mean_rate=None,
                source_effective_date=date(2026, 3, 25),
                source_last_updated_at=None,
                market_scope="commercial_bank",
                channel="non_cash",
                cash_note_band=None,
                created_at=datetime(2026, 3, 25, 0, 0, tzinfo=UTC),
            ),
            ExchangeRateComparisonRecord(
                source_slug="nmb_daily_exchange_rates",
                source_name="NMB Daily Exchange Rates",
                snapshot_date=date(2026, 3, 25),
                instrument_code="USD",
                instrument_name="US Dollar",
                quote_code="TZS",
                buy_rate=Decimal("2530"),
                sell_rate=Decimal("2620"),
                mean_rate=None,
                source_effective_date=date(2026, 3, 25),
                source_last_updated_at=None,
                market_scope="commercial_bank",
                channel="cash",
                cash_note_band="notes_1_20",
                created_at=datetime(2026, 3, 25, 23, 17, tzinfo=UTC),
            ),
        ]

    async def get_latest_bot_snapshot_date(self) -> date | None:
        return date(2026, 3, 25)

    async def list_latest_bot_rates(self, **_: object) -> list[BotExchangeRateRecord]:
        return [
            BotExchangeRateRecord(
                snapshot_date=date(2026, 3, 25),
                instrument_code="USD",
                instrument_name="US DOLLAR",
                quote_code="TZS",
                buy_rate=Decimal("2557.8218"),
                sell_rate=Decimal("2583.4000"),
                mean_rate=Decimal("2570.6109"),
                source_effective_date=date(2026, 3, 25),
                source_last_updated_at=None,
                created_at=datetime(2026, 3, 25, 0, 0, tzinfo=UTC),
            )
        ]

    async def count_bot_rates(self, **_: object) -> int:
        return 1

    async def list_bot_history(self, **_: object) -> list[BotExchangeRateRecord]:
        return await self.list_latest_bot_rates()

    async def list_bot_available_months(self) -> list[BotExchangeRateMonthRecord]:
        return [
            BotExchangeRateMonthRecord(
                month_start=date(2026, 3, 1),
                observation_count=42,
            )
        ]

    async def list_bot_instruments(self) -> list[str]:
        return ["EUR", "USD"]

    async def list_latest_source_comparison(
        self,
        **kwargs: object,
    ) -> list[ExchangeRateComparisonRecord]:
        rows = self._comparison_rows
        channel = kwargs.get("channel")
        cash_note_band = kwargs.get("cash_note_band")
        if channel is not None:
            rows = [row for row in rows if row.channel == channel]
        if cash_note_band is not None:
            rows = [row for row in rows if row.cash_note_band == cash_note_band]
        return rows


async def test_list_bot_latest_maps_repository_rows() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    page = await service.list_bot_latest(instrument_code="USD", limit=10, offset=0)

    assert page.meta.total == 1
    assert page.items[0].snapshot_month_label == "March 2026"
    assert page.items[0].instrument_code == "USD"
    assert page.items[0].mean_rate == Decimal("2570.6109")


async def test_get_bot_filters_includes_month_labels() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    filters = await service.get_bot_filters()

    assert filters.instrument_codes == ["EUR", "USD"]
    assert filters.latest_snapshot_month_label == "March 2026"
    assert filters.available_months[0].month_label == "March 2026"


async def test_get_latest_comparison_keeps_sources_separate() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    comparison = await service.get_latest_comparison(instrument_code="usd")

    assert comparison.instrument_code == "USD"
    assert [item.source_slug for item in comparison.items] == [
        "bot_exchange_rates",
        "crdb_forex",
        "nmb_daily_exchange_rates",
        "nmb_daily_exchange_rates",
    ]
    assert comparison.items[0].market_scope == "official_reference"
    assert comparison.items[1].market_scope == "commercial_bank"


async def test_get_latest_comparison_can_return_channel_specific_rows() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    comparison = await service.get_latest_comparison(
        instrument_code="usd",
        channel="cash",
        cash_note_band="notes_1_20",
    )

    assert comparison.channel == "cash"
    assert comparison.cash_note_band == "notes_1_20"
    assert len(comparison.items) == 1
    assert comparison.items[0].source_slug == "nmb_daily_exchange_rates"


async def test_get_recommendation_prefers_lowest_sell_for_buy_action() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    recommendation = await service.get_recommendation(
        instrument_code="usd",
        customer_action="buy",
    )

    assert recommendation.best_option is not None
    assert recommendation.best_option.source_slug == "crdb_forex"
    assert recommendation.best_option.relevant_rate == Decimal("2615")
    assert recommendation.benchmark is not None
    assert recommendation.benchmark.source_slug == "bot_exchange_rates"


async def test_get_recommendation_prefers_highest_buy_for_sell_action() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    recommendation = await service.get_recommendation(
        instrument_code="usd",
        customer_action="sell",
    )

    assert recommendation.best_option is not None
    assert recommendation.best_option.source_slug == "crdb_forex"
    assert recommendation.best_option.relevant_rate == Decimal("2535")


async def test_get_recommendation_can_target_nmb_cash_band() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    recommendation = await service.get_recommendation(
        instrument_code="usd",
        customer_action="buy",
        channel="cash",
        cash_note_band="notes_1_20",
    )

    assert recommendation.best_option is not None
    assert recommendation.best_option.source_slug == "nmb_daily_exchange_rates"
    assert recommendation.best_option.cash_note_band == "notes_1_20"


async def test_get_spread_summary_orders_smallest_spread_first() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    summary = await service.get_spread_summary(instrument_code="usd")

    assert summary.items[0].source_slug == "bot_exchange_rates"
    assert summary.items[0].spread == Decimal("25.5782")


async def test_get_benchmark_gap_summary_uses_bot_mean_as_reference() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    summary = await service.get_benchmark_gap_summary(
        instrument_code="usd",
        customer_action="buy",
    )

    assert summary.bot_mean_rate == Decimal("2570.6109")
    assert any(item.source_slug == "crdb_forex" for item in summary.items)


async def test_get_staleness_summary_marks_freshest_source() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    summary = await service.get_staleness_summary(instrument_code="usd")

    assert summary.freshest_timestamp is not None
    assert summary.items[0].is_freshest is True


async def test_get_best_rate_summary_returns_buy_and_sell_views() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    summary = await service.get_best_rate_summary(instrument_code="usd")

    assert summary.buy_forex.best_option is not None
    assert summary.sell_forex.best_option is not None


async def test_get_opportunity_summary_compares_against_best_source() -> None:
    service = ExchangeRateService(_FakeExchangeRateRepository())

    summary = await service.get_opportunity_summary(
        instrument_code="usd",
        customer_action="buy",
    )

    assert summary.best_source_slug == "crdb_forex"
    assert all(
        opportunity.best_source_slug == "crdb_forex"
        for opportunity in summary.opportunities
    )
