"""Pydantic schemas for normalized fuel / EWURA API responses."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EwuraFuelObservationRead(BaseModel):
    """One normalized EWURA cap-price row served to the dashboard."""

    id: UUID
    source_id: UUID
    source_label: str
    scraper_run_id: UUID | None
    document_url: str
    content_sha256: str = Field(max_length=64)
    published_date: date | None
    location_id: UUID | None
    canonical_location_name: str | None
    raw_location_text: str
    fuel_type: str
    price: int
    unit: str
    recorded_at: date
    created_at: datetime
