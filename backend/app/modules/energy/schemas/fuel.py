"""Pydantic schemas for normalized fuel / EWURA API responses."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EwuraFuelObservationRead(BaseModel):
    id: UUID
    source_id: UUID
    source_label: str
    scraper_run_id: UUID | None
    document_url: str
    content_sha256: str = Field(max_length=64)
    published_date: date | None
    location_id: UUID | None
    canonical_location_name: str | None
    canonical_region_name: str | None
    raw_location_text: str
    fuel_type: str
    price: int
    price_display: str
    unit: str
    recorded_at: date
    month_label: str
    created_at: datetime


class EwuraFuelLatestPriceRead(BaseModel):
    snapshot_date: date
    snapshot_month_label: str
    previous_snapshot_date: date | None
    previous_snapshot_month_label: str | None
    location_id: UUID | None
    canonical_location_name: str | None
    canonical_region_name: str | None
    raw_location_text: str
    fuel_type: str
    price: int
    price_display: str
    previous_price: int | None
    previous_price_display: str | None
    absolute_change: int | None
    absolute_change_display: str | None
    percent_change: float | None
    unit: str
    document_url: str


class EwuraFuelFiltersRead(BaseModel):
    fuel_types: list[str]
    history_years: list[int]
    latest_snapshot_date: date | None
    latest_snapshot_month_label: str | None


class EwuraFuelLatestSummaryItemRead(BaseModel):
    fuel_type: str
    locations_count: int
    avg_price: int
    avg_price_display: str
    min_price: int
    min_price_display: str
    max_price: int
    max_price_display: str


class EwuraFuelLatestSummaryRead(BaseModel):
    snapshot_date: date
    snapshot_month_label: str
    items: list[EwuraFuelLatestSummaryItemRead]


class EwuraFuelMonthlyTrendRead(BaseModel):
    month_start: date
    month_label: str
    fuel_type: str
    avg_price: int
    avg_price_display: str
    min_price: int
    min_price_display: str
    max_price: int
    max_price_display: str
    locations_count: int


class EwuraFuelHistoryRead(BaseModel):
    filters: dict[str, str | int | None]
    observations: list[EwuraFuelObservationRead]


class EwuraFuelAvailableMonthRead(BaseModel):
    month_start: date
    month_label: str
    observation_count: int
    locations_count: int


class EwuraFuelRollupRead(BaseModel):
    snapshot_date: date
    snapshot_month_label: str
    level: str
    group_name: str
    fuel_type: str
    observations_count: int
    avg_price: int
    avg_price_display: str
    min_price: int
    min_price_display: str
    max_price: int
    max_price_display: str


class EwuraFuelExtremeItemRead(BaseModel):
    location_id: UUID | None
    canonical_location_name: str | None
    raw_location_text: str
    fuel_type: str
    price: int
    price_display: str
    document_url: str


class EwuraFuelLatestExtremesRead(BaseModel):
    snapshot_date: date
    snapshot_month_label: str
    fuel_type: str | None
    cheapest: list[EwuraFuelExtremeItemRead]
    most_expensive: list[EwuraFuelExtremeItemRead]


class EwuraFuelInsightRead(BaseModel):
    title: str
    body: str
    fuel_type: str | None = None


class EwuraFuelDashboardSummaryRead(BaseModel):
    latest_summary: EwuraFuelLatestSummaryRead | None
    latest_prices_preview: list[EwuraFuelLatestPriceRead]
    current_year_trends: list[EwuraFuelMonthlyTrendRead]
    available_months: list[EwuraFuelAvailableMonthRead]
    insights: list[EwuraFuelInsightRead]
