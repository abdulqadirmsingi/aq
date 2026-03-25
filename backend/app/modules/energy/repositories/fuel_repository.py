"""Data access for normalized EWURA fuel observations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Date, cast, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.models.data_point import DataPoint
from app.db.models.reference import Location, Metric, Source
from app.modules.energy.models.fuel import EnergyDetail

_EWURA_METRIC_SLUGS = (
    "ewura_petrol_cap_price",
    "ewura_diesel_cap_price",
    "ewura_kerosene_cap_price",
)


def _at_utc_midnight(value: date) -> datetime:
    return datetime(value.year, value.month, value.day, tzinfo=UTC)


@dataclass(frozen=True)
class FuelObservationRecord:
    id: UUID
    source_id: UUID
    source_label: str
    scraper_run_id: UUID | None
    document_url: str
    content_sha256: str
    published_date: date | None
    location_id: UUID | None
    canonical_location_name: str | None
    canonical_region_name: str | None
    raw_location_text: str
    fuel_type: str
    price: Decimal
    unit: str
    recorded_at: date
    created_at: datetime


@dataclass(frozen=True)
class FuelLatestPriceRecord:
    snapshot_date: date
    previous_snapshot_date: date | None
    location_id: UUID | None
    canonical_location_name: str | None
    canonical_region_name: str | None
    raw_location_text: str
    fuel_type: str
    price: Decimal
    previous_price: Decimal | None
    unit: str
    document_url: str


@dataclass(frozen=True)
class FuelLatestSummaryRecord:
    snapshot_date: date
    fuel_type: str
    locations_count: int
    avg_price: Decimal
    min_price: Decimal
    max_price: Decimal


@dataclass(frozen=True)
class FuelMonthlyTrendRecord:
    month_start: date
    fuel_type: str
    avg_price: Decimal
    min_price: Decimal
    max_price: Decimal
    locations_count: int


@dataclass(frozen=True)
class FuelAvailableMonthRecord:
    month_start: date
    observation_count: int
    locations_count: int


class FuelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_ewura_observations(
        self,
        *,
        limit: int,
        offset: int,
        year: int | None = None,
        month: int | None = None,
        fuel_type: str | None = None,
        location_query: str | None = None,
        location_id: UUID | None = None,
    ) -> list[FuelObservationRecord]:
        stmt = self._observation_select(year, month, fuel_type, location_query)
        if location_id is not None:
            stmt = stmt.where(DataPoint.location_id == location_id)
        rows = await self._session.execute(
            stmt.order_by(DataPoint.recorded_at.desc(), DataPoint.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [self._to_observation_record(row._mapping) for row in rows]

    async def count_ewura_observations(
        self,
        *,
        year: int | None = None,
        month: int | None = None,
        fuel_type: str | None = None,
        location_query: str | None = None,
        location_id: UUID | None = None,
    ) -> int:
        raw_location = DataPoint.extra_data.op("->>")("raw_location_text")
        stmt = select(func.count(DataPoint.id)).select_from(self._base_from_clause())
        if year is not None:
            stmt = stmt.where(extract("year", DataPoint.recorded_at) == year)
        if month is not None:
            stmt = stmt.where(extract("month", DataPoint.recorded_at) == month)
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

    async def get_latest_snapshot_date(self) -> date | None:
        result = await self._session.execute(
            select(cast(func.max(DataPoint.recorded_at), Date)).select_from(
                self._base_from_clause()
            )
        )
        return result.scalar_one_or_none()

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
        current_ts = _at_utc_midnight(snapshot_date)

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
            .where(current_metric.slug.in_(_EWURA_METRIC_SLUGS))
            .where(current_energy.energy_type == "fuel_cap_price")
            .where(current.recorded_at == current_ts)
        )
        if fuel_type is not None:
            stmt = stmt.where(current_energy.fuel_grade == fuel_type)
        if location_query:
            like = f"%{location_query.strip()}%"
            stmt = stmt.where(
                func.coalesce(current_location.name, raw_location).ilike(like)
            )

        result = await self._session.execute(
            stmt.order_by(current_energy.fuel_grade.asc(), func.coalesce(current_location.name, raw_location).asc())
        )
        return [
            FuelLatestPriceRecord(
                snapshot_date=row.snapshot_date,
                previous_snapshot_date=row.previous_snapshot_date,
                location_id=row.location_id,
                canonical_location_name=row.canonical_location_name,
                canonical_region_name=row.canonical_region_name,
                raw_location_text=row.raw_location_text or "",
                fuel_type=row.fuel_type or "",
                price=row.price,
                previous_price=row.previous_price,
                unit=row.unit,
                document_url=row.document_url or "",
            )
            for row in result
        ]

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
            .select_from(self._base_from_clause())
            .where(DataPoint.recorded_at == _at_utc_midnight(snapshot_date))
            .group_by(cast(DataPoint.recorded_at, Date), EnergyDetail.fuel_grade)
            .order_by(EnergyDetail.fuel_grade.asc())
        )
        result = await self._session.execute(stmt)
        return [
            FuelLatestSummaryRecord(
                snapshot_date=row.snapshot_date,
                fuel_type=row.fuel_type,
                locations_count=row.locations_count,
                avg_price=row.avg_price,
                min_price=row.min_price,
                max_price=row.max_price,
            )
            for row in result
        ]

    async def get_current_year_trends(
        self,
        *,
        year: int,
        fuel_type: str | None = None,
    ) -> list[FuelMonthlyTrendRecord]:
        stmt = (
            select(
                cast(func.date_trunc("month", DataPoint.recorded_at), Date).label("month_start"),
                EnergyDetail.fuel_grade.label("fuel_type"),
                func.avg(DataPoint.value_numeric).label("avg_price"),
                func.min(DataPoint.value_numeric).label("min_price"),
                func.max(DataPoint.value_numeric).label("max_price"),
                func.count(DataPoint.id).label("locations_count"),
            )
            .select_from(self._base_from_clause())
            .where(extract("year", DataPoint.recorded_at) == year)
        )
        if fuel_type is not None:
            stmt = stmt.where(EnergyDetail.fuel_grade == fuel_type)
        stmt = (
            stmt.group_by(
                cast(func.date_trunc("month", DataPoint.recorded_at), Date),
                EnergyDetail.fuel_grade,
            )
            .order_by(
                cast(func.date_trunc("month", DataPoint.recorded_at), Date).asc(),
                EnergyDetail.fuel_grade.asc(),
            )
        )
        result = await self._session.execute(stmt)
        return [
            FuelMonthlyTrendRecord(
                month_start=row.month_start,
                fuel_type=row.fuel_type,
                avg_price=row.avg_price,
                min_price=row.min_price,
                max_price=row.max_price,
                locations_count=row.locations_count,
            )
            for row in result
        ]

    async def get_history(
        self,
        *,
        fuel_type: str | None = None,
        location_id: UUID | None = None,
        location_query: str | None = None,
        year: int | None = None,
        offset: int = 0,
        limit: int = 500,
    ) -> list[FuelObservationRecord]:
        stmt = self._observation_select(year, None, fuel_type, location_query)
        if location_id is not None:
            stmt = stmt.where(DataPoint.location_id == location_id)
        rows = await self._session.execute(
            stmt.order_by(DataPoint.recorded_at.desc(), DataPoint.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [self._to_observation_record(row._mapping) for row in rows]

    async def get_available_months(self) -> list[FuelAvailableMonthRecord]:
        stmt = (
            select(
                cast(func.date_trunc("month", DataPoint.recorded_at), Date).label("month_start"),
                func.count(DataPoint.id).label("observation_count"),
                func.count(func.distinct(DataPoint.location_id)).label("locations_count"),
            )
            .select_from(self._base_from_clause())
            .group_by(cast(func.date_trunc("month", DataPoint.recorded_at), Date))
            .order_by(cast(func.date_trunc("month", DataPoint.recorded_at), Date).desc())
        )
        result = await self._session.execute(stmt)
        return [
            FuelAvailableMonthRecord(
                month_start=row.month_start,
                observation_count=row.observation_count,
                locations_count=row.locations_count,
            )
            for row in result
        ]

    def _observation_select(
        self,
        year: int | None,
        month: int | None,
        fuel_type: str | None,
        location_query: str | None,
    ):
        parent_location = aliased(Location)
        raw_location = DataPoint.extra_data.op("->>")("raw_location_text")
        document_url = DataPoint.extra_data.op("->>")("document_url")
        published_date = cast(DataPoint.extra_data.op("->>")("published_date"), Date)
        content_sha256 = DataPoint.ingestion_metadata.op("->>")("content_sha256")
        stmt = (
            select(
                DataPoint.id.label("id"),
                DataPoint.source_id.label("source_id"),
                Source.name.label("source_label"),
                DataPoint.scraper_run_id.label("scraper_run_id"),
                document_url.label("document_url"),
                content_sha256.label("content_sha256"),
                published_date.label("published_date"),
                DataPoint.location_id.label("location_id"),
                Location.name.label("canonical_location_name"),
                parent_location.name.label("canonical_region_name"),
                raw_location.label("raw_location_text"),
                EnergyDetail.fuel_grade.label("fuel_type"),
                DataPoint.value_numeric.label("price"),
                func.coalesce(DataPoint.unit_override, Metric.unit, "TZS/Litre").label("unit"),
                cast(DataPoint.recorded_at, Date).label("recorded_at"),
                DataPoint.created_at.label("created_at"),
            )
            .select_from(self._base_from_clause(parent_location=parent_location))
        )
        if year is not None:
            stmt = stmt.where(extract("year", DataPoint.recorded_at) == year)
        if month is not None:
            stmt = stmt.where(extract("month", DataPoint.recorded_at) == month)
        if fuel_type is not None:
            stmt = stmt.where(EnergyDetail.fuel_grade == fuel_type)
        if location_query:
            like = f"%{location_query.strip()}%"
            stmt = stmt.where(func.coalesce(Location.name, raw_location).ilike(like))
        return stmt

    @staticmethod
    def _base_from_clause(parent_location: Location | None = None):
        base = (
            DataPoint.__table__
            .join(Metric.__table__, DataPoint.metric_id == Metric.id)
            .join(
                EnergyDetail.__table__,
                (EnergyDetail.data_point_id == DataPoint.id)
                & (EnergyDetail.data_point_recorded_at == DataPoint.recorded_at),
            )
            .join(Source.__table__, DataPoint.source_id == Source.id)
            .outerjoin(Location.__table__, DataPoint.location_id == Location.id)
        )
        if parent_location is not None:
            base = base.outerjoin(parent_location.__table__, Location.parent_id == parent_location.__table__.c.id)
        return base

    @staticmethod
    def _to_observation_record(row: Any) -> FuelObservationRecord:
        return FuelObservationRecord(
            id=row["id"],
            source_id=row["source_id"],
            source_label=row["source_label"] or "EWURA",
            scraper_run_id=row["scraper_run_id"],
            document_url=row["document_url"] or "",
            content_sha256=row["content_sha256"] or "",
            published_date=row["published_date"],
            location_id=row["location_id"],
            canonical_location_name=row["canonical_location_name"],
            canonical_region_name=row["canonical_region_name"],
            raw_location_text=row["raw_location_text"] or "",
            fuel_type=row["fuel_type"] or "",
            price=row["price"],
            unit=row["unit"],
            recorded_at=row["recorded_at"],
            created_at=row["created_at"],
        )
