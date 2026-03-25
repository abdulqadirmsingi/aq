"""Shared record types and query helpers for EWURA fuel repositories."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Date, cast, extract, func, select
from sqlalchemy.orm import aliased

from app.db.models.data_point import DataPoint
from app.db.models.reference import Location, Metric, Source
from app.modules.energy.models.fuel import EnergyDetail

EWURA_METRIC_SLUGS = (
    "ewura_petrol_cap_price",
    "ewura_diesel_cap_price",
    "ewura_kerosene_cap_price",
)


def at_utc_midnight(value: date) -> datetime:
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


def build_base_from_clause(parent_location: Any | None = None):
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
        base = base.outerjoin(
            parent_location.__table__,
            Location.parent_id == parent_location.__table__.c.id,
        )
    return base


def build_observation_select(
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
        .select_from(build_base_from_clause(parent_location=parent_location))
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


def to_observation_record(row: Any) -> FuelObservationRecord:
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
