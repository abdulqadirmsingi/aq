"""Pydantic schemas for fuel / EWURA API responses."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EwuraFuelObservationRead(BaseModel):
    """One persisted cap-price row (served to the dashboard)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_label: str
    document_url: str
    content_sha256: str = Field(max_length=64)
    published_date: date | None
    location: str
    fuel_type: str
    price: int
    unit: str
    recorded_at: date
    created_at: datetime
