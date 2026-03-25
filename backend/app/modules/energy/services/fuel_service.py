"""Business logic for normalized EWURA fuel responses."""

from __future__ import annotations

import calendar
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from app.common.pagination import Page, build_page
from app.modules.energy.repositories.fuel_repository import (
    FuelAvailableMonthRecord,
    FuelLatestPriceRecord,
    FuelLatestSummaryRecord,
    FuelMonthlyTrendRecord,
    FuelObservationRecord,
    FuelRepository,
)
from app.modules.energy.schemas.fuel import (
    EwuraFuelAvailableMonthRead,
    EwuraFuelDashboardSummaryRead,
    EwuraFuelExtremeItemRead,
    EwuraFuelInsightRead,
    EwuraFuelLatestPriceRead,
    EwuraFuelLatestExtremesRead,
    EwuraFuelLatestSummaryItemRead,
    EwuraFuelLatestSummaryRead,
    EwuraFuelMonthlyTrendRead,
    EwuraFuelObservationRead,
    EwuraFuelRollupRead,
)


class FuelService:
    def __init__(self, repository: FuelRepository) -> None:
        self._repository = repository

    async def list_ewura_observations(
        self,
        *,
        limit: int,
        offset: int,
        year: int | None,
        month: int | None,
        fuel_type: str | None,
        location_query: str | None,
        location_id: UUID | None = None,
    ) -> Page[EwuraFuelObservationRead]:
        rows = await self._repository.list_ewura_observations(
            limit=limit,
            offset=offset,
            year=year,
            month=month,
            fuel_type=fuel_type,
            location_query=location_query,
            location_id=location_id,
        )
        total = await self._repository.count_ewura_observations(
            year=year,
            month=month,
            fuel_type=fuel_type,
            location_query=location_query,
            location_id=location_id,
        )
        return build_page(
            [self._to_observation(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_latest_prices(
        self,
        *,
        fuel_type: str | None,
        location_query: str | None,
    ) -> list[EwuraFuelLatestPriceRead]:
        snapshot_date = await self._repository.get_latest_snapshot_date()
        if snapshot_date is None:
            return []
        rows = await self._repository.list_latest_prices(
            snapshot_date=snapshot_date,
            fuel_type=fuel_type,
            location_query=location_query,
        )
        return [self._to_latest_price(row) for row in rows]

    async def get_latest_summary(self) -> EwuraFuelLatestSummaryRead | None:
        snapshot_date = await self._repository.get_latest_snapshot_date()
        if snapshot_date is None:
            return None
        rows = await self._repository.get_latest_summary(snapshot_date=snapshot_date)
        return EwuraFuelLatestSummaryRead(
            snapshot_date=snapshot_date,
            snapshot_month_label=self._month_label(snapshot_date),
            items=[self._to_latest_summary_item(row) for row in rows],
        )

    async def get_current_year_trends(
        self,
        *,
        year: int | None,
        fuel_type: str | None,
    ) -> list[EwuraFuelMonthlyTrendRead]:
        effective_year = year or datetime.now(UTC).year
        rows = await self._repository.get_current_year_trends(
            year=effective_year,
            fuel_type=fuel_type,
        )
        return [self._to_monthly_trend(row) for row in rows]

    async def get_history(
        self,
        *,
        fuel_type: str | None,
        location_id: UUID | None,
        location_query: str | None,
        year: int | None,
        offset: int,
        limit: int,
    ) -> Page[EwuraFuelObservationRead]:
        rows = await self._repository.get_history(
            fuel_type=fuel_type,
            location_id=location_id,
            location_query=location_query,
            year=year,
            offset=offset,
            limit=limit,
        )
        total = await self._repository.count_ewura_observations(
            year=year,
            fuel_type=fuel_type,
            location_query=location_query,
            location_id=location_id,
        )
        return build_page(
            [self._to_observation(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_available_months(self) -> list[EwuraFuelAvailableMonthRead]:
        rows = await self._repository.get_available_months()
        return [self._to_available_month(row) for row in rows]

    async def get_rollups(
        self,
        *,
        level: str,
        fuel_type: str | None,
    ) -> list[EwuraFuelRollupRead]:
        latest = await self.get_latest_prices(fuel_type=fuel_type, location_query=None)
        grouped: dict[tuple[str, str], list[EwuraFuelLatestPriceRead]] = {}
        for item in latest:
            group_name = self._group_name(item, level)
            if group_name is None:
                continue
            grouped.setdefault((group_name, item.fuel_type), []).append(item)
        rollups: list[EwuraFuelRollupRead] = []
        for (group_name, current_fuel_type), items in sorted(grouped.items()):
            prices = [item.price for item in items]
            if not prices:
                continue
            snapshot_date = items[0].snapshot_date
            avg_price = int(sum(prices) / len(prices))
            min_price = min(prices)
            max_price = max(prices)
            rollups.append(
                EwuraFuelRollupRead(
                    snapshot_date=snapshot_date,
                    snapshot_month_label=self._month_label(snapshot_date),
                    level=level,
                    group_name=group_name,
                    fuel_type=current_fuel_type,
                    observations_count=len(items),
                    avg_price=avg_price,
                    avg_price_display=self._price_display(avg_price, items[0].unit),
                    min_price=min_price,
                    min_price_display=self._price_display(min_price, items[0].unit),
                    max_price=max_price,
                    max_price_display=self._price_display(max_price, items[0].unit),
                )
            )
        return rollups

    async def get_latest_extremes(
        self,
        *,
        fuel_type: str | None,
        top: int,
    ) -> EwuraFuelLatestExtremesRead | None:
        latest = await self.get_latest_prices(fuel_type=fuel_type, location_query=None)
        if not latest:
            return None
        sorted_prices = sorted(latest, key=lambda item: (item.price, item.raw_location_text))
        return EwuraFuelLatestExtremesRead(
            snapshot_date=latest[0].snapshot_date,
            snapshot_month_label=latest[0].snapshot_month_label,
            fuel_type=fuel_type,
            cheapest=[self._to_extreme_item(item) for item in sorted_prices[:top]],
            most_expensive=[self._to_extreme_item(item) for item in sorted_prices[-top:][::-1]],
        )

    async def get_insights(self) -> list[EwuraFuelInsightRead]:
        latest_summary = await self.get_latest_summary()
        latest_prices = await self.get_latest_prices(fuel_type=None, location_query=None)
        trends = await self.get_current_year_trends(year=None, fuel_type=None)
        if latest_summary is None or not latest_prices:
            return []
        insights: list[EwuraFuelInsightRead] = []
        for item in latest_summary.items:
            matching_prices = [price for price in latest_prices if price.fuel_type == item.fuel_type]
            changed = [price for price in matching_prices if price.percent_change is not None]
            if changed:
                avg_change = round(
                    sum(price.percent_change for price in changed if price.percent_change is not None)
                    / len(changed),
                    2,
                )
                direction = "increased" if avg_change > 0 else "decreased" if avg_change < 0 else "stayed flat"
                insights.append(
                    EwuraFuelInsightRead(
                        title=f"{item.fuel_type.title()} month-over-month movement",
                        body=(
                            f"In {latest_summary.snapshot_month_label}, average {item.fuel_type} prices "
                            f"{direction} by {abs(avg_change):.2f}% across {item.locations_count} locations."
                        ),
                        fuel_type=item.fuel_type,
                    )
                )
        if trends:
            latest_month = max(trends, key=lambda row: row.month_start)
            latest_month_rows = [row for row in trends if row.month_start == latest_month.month_start]
            if latest_month_rows:
                top_fuel = max(latest_month_rows, key=lambda row: row.avg_price)
                insights.append(
                    EwuraFuelInsightRead(
                        title="Highest average fuel this month",
                        body=(
                            f"{top_fuel.fuel_type.title()} had the highest average price in "
                            f"{top_fuel.month_label} at {top_fuel.avg_price_display}."
                        ),
                        fuel_type=top_fuel.fuel_type,
                    )
                )
        return insights

    async def get_dashboard_summary(self) -> EwuraFuelDashboardSummaryRead:
        latest_summary = await self.get_latest_summary()
        latest_prices = await self.get_latest_prices(fuel_type=None, location_query=None)
        trends = await self.get_current_year_trends(year=None, fuel_type=None)
        available_months = await self.get_available_months()
        insights = await self.get_insights()
        return EwuraFuelDashboardSummaryRead(
            latest_summary=latest_summary,
            latest_prices_preview=latest_prices[:12],
            current_year_trends=trends,
            available_months=available_months,
            insights=insights,
        )

    def _to_observation(self, row: FuelObservationRecord) -> EwuraFuelObservationRead:
        price = self._to_int(row.price)
        return EwuraFuelObservationRead(
            id=row.id,
            source_id=row.source_id,
            source_label=row.source_label,
            scraper_run_id=row.scraper_run_id,
            document_url=row.document_url,
            content_sha256=row.content_sha256,
            published_date=row.published_date,
            location_id=row.location_id,
            canonical_location_name=row.canonical_location_name,
            canonical_region_name=row.canonical_region_name,
            raw_location_text=row.raw_location_text,
            fuel_type=row.fuel_type,
            price=price,
            price_display=self._price_display(price, row.unit),
            unit=row.unit,
            recorded_at=row.recorded_at,
            month_label=self._month_label(row.recorded_at),
            created_at=row.created_at,
        )

    def _to_latest_price(self, row: FuelLatestPriceRecord) -> EwuraFuelLatestPriceRead:
        price = self._to_int(row.price)
        previous_price = self._to_int(row.previous_price) if row.previous_price is not None else None
        absolute_change = price - previous_price if previous_price is not None else None
        percent_change = (
            round((absolute_change / previous_price) * 100, 2)
            if previous_price not in (None, 0) and absolute_change is not None
            else None
        )
        return EwuraFuelLatestPriceRead(
            snapshot_date=row.snapshot_date,
            snapshot_month_label=self._month_label(row.snapshot_date),
            previous_snapshot_date=row.previous_snapshot_date,
            previous_snapshot_month_label=(
                self._month_label(row.previous_snapshot_date)
                if row.previous_snapshot_date is not None
                else None
            ),
            location_id=row.location_id,
            canonical_location_name=row.canonical_location_name,
            canonical_region_name=row.canonical_region_name,
            raw_location_text=row.raw_location_text,
            fuel_type=row.fuel_type,
            price=price,
            price_display=self._price_display(price, row.unit),
            previous_price=previous_price,
            previous_price_display=(
                self._price_display(previous_price, row.unit)
                if previous_price is not None
                else None
            ),
            absolute_change=absolute_change,
            absolute_change_display=(
                self._signed_price_display(absolute_change, row.unit)
                if absolute_change is not None
                else None
            ),
            percent_change=percent_change,
            unit=row.unit,
            document_url=row.document_url,
        )

    def _to_latest_summary_item(
        self,
        row: FuelLatestSummaryRecord,
    ) -> EwuraFuelLatestSummaryItemRead:
        avg_price = self._to_int(row.avg_price)
        min_price = self._to_int(row.min_price)
        max_price = self._to_int(row.max_price)
        return EwuraFuelLatestSummaryItemRead(
            fuel_type=row.fuel_type,
            locations_count=row.locations_count,
            avg_price=avg_price,
            avg_price_display=self._price_display(avg_price, "TZS/Litre"),
            min_price=min_price,
            min_price_display=self._price_display(min_price, "TZS/Litre"),
            max_price=max_price,
            max_price_display=self._price_display(max_price, "TZS/Litre"),
        )

    def _to_monthly_trend(self, row: FuelMonthlyTrendRecord) -> EwuraFuelMonthlyTrendRead:
        avg_price = self._to_int(row.avg_price)
        min_price = self._to_int(row.min_price)
        max_price = self._to_int(row.max_price)
        return EwuraFuelMonthlyTrendRead(
            month_start=row.month_start,
            month_label=self._month_label(row.month_start),
            fuel_type=row.fuel_type,
            avg_price=avg_price,
            avg_price_display=self._price_display(avg_price, "TZS/Litre"),
            min_price=min_price,
            min_price_display=self._price_display(min_price, "TZS/Litre"),
            max_price=max_price,
            max_price_display=self._price_display(max_price, "TZS/Litre"),
            locations_count=row.locations_count,
        )

    def _to_available_month(self, row: FuelAvailableMonthRecord) -> EwuraFuelAvailableMonthRead:
        return EwuraFuelAvailableMonthRead(
            month_start=row.month_start,
            month_label=self._month_label(row.month_start),
            observation_count=row.observation_count,
            locations_count=row.locations_count,
        )

    def _to_extreme_item(self, row: EwuraFuelLatestPriceRead) -> EwuraFuelExtremeItemRead:
        return EwuraFuelExtremeItemRead(
            location_id=row.location_id,
            canonical_location_name=row.canonical_location_name,
            raw_location_text=row.raw_location_text,
            fuel_type=row.fuel_type,
            price=row.price,
            price_display=row.price_display,
            document_url=row.document_url,
        )

    @staticmethod
    def _group_name(item: EwuraFuelLatestPriceRead, level: str) -> str | None:
        if level == "city":
            return item.canonical_location_name or item.raw_location_text
        if level == "region":
            return item.canonical_region_name
        return None

    @staticmethod
    def _to_int(value: Decimal | int | None) -> int:
        if value is None:
            return 0
        return int(value)

    @staticmethod
    def _month_label(value: date | None) -> str | None:
        if value is None:
            return None
        return f"{calendar.month_name[value.month]} {value.year}"

    @staticmethod
    def _price_display(value: int, unit: str) -> str:
        return f"{value:,.0f} {unit}"

    @staticmethod
    def _signed_price_display(value: int, unit: str) -> str:
        sign = "+" if value >= 0 else "-"
        return f"{sign}{abs(value):,.0f} {unit}"
