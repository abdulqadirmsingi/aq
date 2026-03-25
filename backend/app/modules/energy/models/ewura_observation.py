"""EWURA cap-price rows persisted by the scraper worker (read by API)."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EwuraFuelObservation(Base):
    __tablename__ = "ewura_fuel_observations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    source_label: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="EWURA",
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="SET NULL"),
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="SET NULL"),
    )
    scraper_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scraper_runs.id", ondelete="SET NULL"),
    )
    document_url: Mapped[str] = mapped_column(Text(), nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    published_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(32), nullable=False)
    price: Mapped[int] = mapped_column(Integer(), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False, default="TZS/Litre")
    recorded_at: Mapped[date] = mapped_column(Date(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
