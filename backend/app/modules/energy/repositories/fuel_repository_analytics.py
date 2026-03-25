"""Analytical repository methods for EWURA fuel data."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, cast, extract, func, select
from sqlalchemy.orm import aliased

from app.db.models.data_point import DataPoint
from app.db.models.reference import Location, Metric, Source
from app.modules.energy.models.fuel import EnergyDetail
from app.modules.energy.repositories.fuel_repository_shared import (
    EWURA_METRIC_SLUGS,
    FuelAvailableMonthRecord,
    FuelLatestPriceRecord,
    FuelLatestSummaryRecord,
    FuelMonthlyTrendRecord,
    at_utc_midnight,
    build_base_from_clause,
)


class FuelAnalyticsRepositoryMixin:
    async def get_latest_snapshot_date(self) -> date | None:
        snapshot_date_expr = cast(DataPoint.recorded_at, Date)
        result = await self._session.execute(
            select(
                snapshot_date_expr.label("snapshot_date"),
                func.count(func.distinct(DataPoint.location_id)).label("locations_count"),
                func.count(func.distinct(Metric.slug)).label("metrics_count"),
            )
            .select_from(build_base_from_clause())
            .group_by(snapshot_date_expr)
            .order_by(snapshot_date_expr.desc())
        )
        rows = result.mappings().all()
        if not rows:
            return None

        max_locations = max(int(row["locations_count"] or 0) for row in rows)
        threshold = max(1, int(max_locations * 0.8))
        for row in rows:
            if (
                int(row["locations_count"] or 0) >= threshold
                and int(row["metrics_count"] or 0) == len(EWURA_METRIC_SLUGS)
            ):
                return row["snapshot_date"]

        return rows[0]["snapshot_date"]

    async def list_latest_prices(
        self,
        *,
        snapshot_date: date,
        fuel_type: str | None = None,
        location_query: str | None = None,
    ) -> list[FuelLatestPriceRecord]:
        current = aliased(DataPoint)
        previous = aliased(DataPoint)
        current_metric = aliased(Metric)
        current_energy = aliased(EnergyDetail)
        current_location = aliased(Location)
        current_parent_location = aliased(Location)
        current_source = aliased(Source)
        raw_location = current.extra_data.op("->>")("raw_location_text")
        document_url = current.extra_data.op("->>")("document_url")
        current_ts = at_utc_midnight(snapshot_date)

        previous_price_sq = (
            select(previous.value_numeric)
            .join(Metric, previous.metric_id == Metric.id)
            .where(previous.metric_id == current.metric_id)
            .where(previous.location_id == current.location_id)
            .where(previous.source_id == current.source_id)
            .where(previous.is_current.is_(True))
            .where(previous.recorded_at < current.recorded_at)
            .order_by(previous.recorded_at.desc())
            .limit(1)
            .scalar_subquery()
        )
        previous_date_sq = (
            select(cast(previous.recorded_at, Date))
            .where(previous.metric_id == current.metric_id)
            .where(previous.location_id == current.location_id)
            .where(previous.source_id == current.source_id)
            .where(previous.is_current.is_(True))
            .where(previous.recorded_at < current.recorded_at)
            .order_by(previous.recorded_at.desc())
            .limit(1)
            .scalar_subquery()
        )

        stmt = (
            select(
                cast(current.recorded_at, Date).label("snapshot_date"),
                previous_date_sq.label("previous_snapshot_date"),
                current.location_id.label("location_id"),
                current_location.name.label("canonical_location_name"),
                current_parent_location.name.label("canonical_region_name"),
                raw_location.label("raw_location_text"),
                current_energy.fuel_grade.label("fuel_type"),
                current.value_numeric.label("price"),
                previous_price_sq.label("previous_price"),
                func.coalesce(current.unit_override, current_metric.unit, "TZS/Litre").label("unit"),
                document_url.label("document_url"),
            )
            .select_from(current)
            .join(current_metric, current.metric_id == current_metric.id)
            .join(
                current_energy,
                (current_energy.data_point_id == current.id)
                & (current_energy.data_point_recorded_at == current.recorded_at),
            )
            .join(current_source, current.source_id == current_source.id)
            .outerjoin(current_location, current.location_id == current_location.id)
            .outerjoin(current_parent_location, current_location.parent_id == current_parent_location.id)
            .where(current.is_current.is_(True))
            .where(current_metric.slug.in_(EWURA_METRIC_SLUGS))
            .where(current_energy.energy_type == "fuel_cap_price")
            .where(current.recorded_at == current_ts)
        )
        if fuel_type is not None:
            stmt = stmt.where(current_energy.fuel_grade == fuel_type)
        if location_query:
            stmt = stmt.where(
                func.coalesce(current_location.name, raw_location).ilike(
                    f"%{location_query.strip()}%"
                )
            )
        result = await self._session.execute(
            stmt.order_by(
                current_energy.fuel_grade.asc(),
                func.coalesce(current_location.name, raw_location).asc(),
            )
        )
        return [FuelLatestPriceRecord(**row._mapping) for row in result]

    async def get_latest_summary(
        self,
        *,
        snapshot_date: date,
    ) -> list[FuelLatestSummaryRecord]:
        stmt = (
            select(
                cast(DataPoint.recorded_at, Date).label("snapshot_date"),
                EnergyDetail.fuel_grade.label("fuel_type"),
                func.count(DataPoint.id).label("locations_count"),
                func.avg(DataPoint.value_numeric).label("avg_price"),
                func.min(DataPoint.value_numeric).label("min_price"),
                func.max(DataPoint.value_numeric).label("max_price"),
            )
            .select_from(build_base_from_clause())
            .where(DataPoint.recorded_at == at_utc_midnight(snapshot_date))
            .group_by(cast(DataPoint.recorded_at, Date), EnergyDetail.fuel_grade)
            .order_by(EnergyDetail.fuel_grade.asc())
        )
        result = await self._session.execute(stmt)
        return [FuelLatestSummaryRecord(**row._mapping) for row in result]

    async def get_current_year_trends(
        self,
        *,
        year: int,
        fuel_type: str | None = None,
    ) -> list[FuelMonthlyTrendRecord]:
        month_start_expr = cast(func.date_trunc("month", DataPoint.recorded_at), Date)
        stmt = (
            select(
                month_start_expr.label("month_start"),
                EnergyDetail.fuel_grade.label("fuel_type"),
                func.avg(DataPoint.value_numeric).label("avg_price"),
                func.min(DataPoint.value_numeric).label("min_price"),
                func.max(DataPoint.value_numeric).label("max_price"),
                func.count(DataPoint.id).label("locations_count"),
            )
            .select_from(build_base_from_clause())
            .where(extract("year", DataPoint.recorded_at) == year)
        )
        if fuel_type is not None:
            stmt = stmt.where(EnergyDetail.fuel_grade == fuel_type)
        result = await self._session.execute(
            stmt.group_by(
                month_start_expr,
                EnergyDetail.fuel_grade,
            ).order_by(
                month_start_expr.asc(),
                EnergyDetail.fuel_grade.asc(),
            )
        )
        return [FuelMonthlyTrendRecord(**row._mapping) for row in result]

    async def get_available_months(self) -> list[FuelAvailableMonthRecord]:
        month_start_expr = cast(func.date_trunc("month", DataPoint.recorded_at), Date)
        stmt = (
            select(
                month_start_expr.label("month_start"),
                func.count(DataPoint.id).label("observation_count"),
                func.count(func.distinct(DataPoint.location_id)).label("locations_count"),
            )
            .select_from(build_base_from_clause())
            .group_by(month_start_expr)
            .order_by(month_start_expr.desc())
        )
        result = await self._session.execute(stmt)
        return [FuelAvailableMonthRecord(**row._mapping) for row in result]
