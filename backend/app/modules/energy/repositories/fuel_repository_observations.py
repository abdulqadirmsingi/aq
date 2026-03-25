"""Observation-oriented repository methods for EWURA fuel data."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Date, cast, func, select

from app.db.models.data_point import DataPoint
from app.db.models.reference import Location
from app.modules.energy.models.fuel import EnergyDetail
from app.modules.energy.repositories.fuel_repository_shared import (
    ENERGY_TYPE_BY_MARKET,
    FuelObservationRecord,
    build_base_from_clause,
    build_observation_select,
    to_observation_record,
)


class FuelObservationRepositoryMixin:
    async def list_ewura_observations(
        self,
        *,
        limit: int,
        offset: int,
        year: int | None = None,
        month: int | None = None,
        fuel_type: str | None = None,
        location_query: str | None = None,
        market_segment: str = "retail",
        location_id: UUID | None = None,
    ) -> list[FuelObservationRecord]:
        stmt = build_observation_select(year, month, fuel_type, location_query, market_segment)
        if location_id is not None:
            stmt = stmt.where(DataPoint.location_id == location_id)
        rows = await self._session.execute(
            stmt.order_by(DataPoint.recorded_at.desc(), DataPoint.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [to_observation_record(row._mapping) for row in rows]

    async def count_ewura_observations(
        self,
        *,
        year: int | None = None,
        month: int | None = None,
        fuel_type: str | None = None,
        location_query: str | None = None,
        market_segment: str = "retail",
        location_id: UUID | None = None,
        exclude_snapshot_date: date | None = None,
    ) -> int:
        raw_location = DataPoint.extra_data.op("->>")("raw_location_text")
        stmt = (
            select(func.count(DataPoint.id))
            .select_from(build_base_from_clause())
            .where(EnergyDetail.energy_type == ENERGY_TYPE_BY_MARKET[market_segment])
        )
        if year is not None:
            stmt = stmt.where(func.extract("year", DataPoint.recorded_at) == year)
        if month is not None:
            stmt = stmt.where(func.extract("month", DataPoint.recorded_at) == month)
        if exclude_snapshot_date is not None:
            stmt = stmt.where(cast(DataPoint.recorded_at, Date) != exclude_snapshot_date)
        if fuel_type is not None:
            stmt = stmt.where(EnergyDetail.fuel_grade == fuel_type)
        if location_query:
            stmt = stmt.where(
                func.coalesce(Location.name, raw_location).ilike(f"%{location_query.strip()}%")
            )
        if location_id is not None:
            stmt = stmt.where(DataPoint.location_id == location_id)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def get_history(
        self,
        *,
        fuel_type: str | None = None,
        location_id: UUID | None = None,
        location_query: str | None = None,
        year: int | None = None,
        market_segment: str = "retail",
        exclude_snapshot_date: date | None = None,
        offset: int = 0,
        limit: int = 500,
    ) -> list[FuelObservationRecord]:
        stmt = build_observation_select(
            year,
            None,
            fuel_type,
            location_query,
            market_segment,
            exclude_snapshot_date,
        )
        if location_id is not None:
            stmt = stmt.where(DataPoint.location_id == location_id)
        rows = await self._session.execute(
            stmt.order_by(DataPoint.recorded_at.desc(), DataPoint.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [to_observation_record(row._mapping) for row in rows]
