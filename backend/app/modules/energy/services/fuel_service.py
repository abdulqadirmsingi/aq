"""Business logic for normalized EWURA fuel responses."""

from __future__ import annotations

import calendar
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

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
    EwuraFuelHistoryRead,
    EwuraFuelLatestPriceRead,
    EwuraFuelLatestSummaryItemRead,
    EwuraFuelLatestSummaryRead,
    EwuraFuelMonthlyTrendRead,
    EwuraFuelObservationRead,
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
    ) -> list[EwuraFuelObservationRead]:
        rows = await self._repository.list_ewura_observations(
            limit=limit,
            offset=offset,
            year=year,
            month=month,
            fuel_type=fuel_type,
            location_query=location_query,
        )
        return [self._to_observation(row) for row in rows]

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
        limit: int,
    ) -> EwuraFuelHistoryRead:
        rows = await self._repository.get_history(
            fuel_type=fuel_type,
            location_id=location_id,
            location_query=location_query,
            year=year,
            limit=limit,
        )
        return EwuraFuelHistoryRead(
            filters={
                "fuel_type": fuel_type,
                "location_id": str(location_id) if location_id else None,
                "location_query": location_query,
                "year": year,
            },
            observations=[self._to_observation(row) for row in rows],
        )

    async def get_available_months(self) -> list[EwuraFuelAvailableMonthRead]:
        rows = await self._repository.get_available_months()
        return [self._to_available_month(row) for row in rows]

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
