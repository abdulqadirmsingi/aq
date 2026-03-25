"""Core service methods for normalized EWURA fuel responses."""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from app.common.pagination import Page, build_page
from app.modules.energy.repositories.fuel_repository import (
    FuelRepository,
)
from app.modules.energy.schemas.fuel import (
    EwuraFuelAvailableMonthRead,
    EwuraFuelDashboardSummaryRead,
    EwuraFuelFiltersRead,
    EwuraFuelLatestPriceRead,
    EwuraFuelLatestSummaryRead,
    EwuraFuelObservationRead,
    EwuraFuelMonthlyTrendRead,
)
from app.modules.energy.services.fuel_service_formatting import FuelFormattingMixin
from app.modules.energy.services.fuel_service_insights import FuelInsightServiceMixin


class FuelService(FuelInsightServiceMixin, FuelFormattingMixin):
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

    async def list_latest_prices_page(
        self,
        *,
        fuel_type: str | None,
        location_query: str | None,
        limit: int,
        offset: int,
    ) -> Page[EwuraFuelLatestPriceRead]:
        snapshot_date = await self._repository.get_latest_snapshot_date()
        if snapshot_date is None:
            return build_page([], total=0, limit=limit, offset=offset)

        rows = await self._repository.list_latest_prices(
            snapshot_date=snapshot_date,
            fuel_type=fuel_type,
            location_query=location_query,
            limit=limit,
            offset=offset,
        )
        total = await self._repository.count_latest_prices(
            snapshot_date=snapshot_date,
            fuel_type=fuel_type,
            location_query=location_query,
        )
        return build_page(
            [self._to_latest_price(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

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
        latest_snapshot_date = await self._repository.get_latest_snapshot_date()
        effective_year = year or (
            latest_snapshot_date.year if latest_snapshot_date is not None else datetime.now(UTC).year
        )
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
        latest_snapshot_date = await self._repository.get_latest_snapshot_date()
        rows = await self._repository.get_history(
            fuel_type=fuel_type,
            location_id=location_id,
            location_query=location_query,
            year=year,
            exclude_snapshot_date=latest_snapshot_date,
            offset=offset,
            limit=limit,
        )
        total = await self._repository.count_ewura_observations(
            year=year,
            fuel_type=fuel_type,
            location_query=location_query,
            location_id=location_id,
            exclude_snapshot_date=latest_snapshot_date,
        )
        return build_page(
            [self._to_observation(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_filters(self) -> EwuraFuelFiltersRead:
        latest_snapshot_date = await self._repository.get_latest_snapshot_date()
        fuel_types = await self._repository.list_available_fuel_types()
        history_years = await self._repository.list_history_years(
            exclude_snapshot_date=latest_snapshot_date,
        )
        return EwuraFuelFiltersRead(
            fuel_types=fuel_types,
            history_years=history_years,
            latest_snapshot_date=latest_snapshot_date,
            latest_snapshot_month_label=self._month_label(latest_snapshot_date),
        )

    async def get_available_months(self) -> list[EwuraFuelAvailableMonthRead]:
        rows = await self._repository.get_available_months()
        return [self._to_available_month(row) for row in rows]
