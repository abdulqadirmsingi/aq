"""Schemas for EWURA scraper run and ingestion log inspection."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EwuraFuelRunRead(BaseModel):
    id: UUID
    scraper_name: str
    trigger_type: str
    status: str
    category_slug: str | None
    source_name: str | None
    started_at: datetime | None
    finished_at: datetime | None
    records_read: int
    records_inserted: int
    records_updated: int
    records_rejected: int
    error_message: str | None
    run_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class EwuraFuelRunLogRead(BaseModel):
    id: UUID
    scraper_run_id: UUID
    data_point_id: UUID | None
    data_point_recorded_at: datetime | None
    level: str
    event_type: str
    message: str
    details: dict[str, object]
    created_at: datetime
