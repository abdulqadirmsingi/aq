from datetime import UTC, date, datetime
from decimal import Decimal

from app.modules.money.repositories.exchange_rate_repository import (
    BotExchangeRateMonthRecord,
    BotExchangeRateRecord,
)
from app.modules.money.services.exchange_rate_service import ExchangeRateService


class _FakeExchangeRateRepository:
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
