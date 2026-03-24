from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

from .enums import ScraperRunStatus


class ScraperRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scraper_runs"

    scraper_name: Mapped[str] = mapped_column(String(120), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[ScraperRunStatus] = mapped_column(
        Enum(ScraperRunStatus, name="scraper_run_status_enum"),
        nullable=False,
        default=ScraperRunStatus.PENDING,
        server_default=ScraperRunStatus.PENDING.value,
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("data_categories.id", ondelete="SET NULL"),
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_read: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    records_inserted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    records_updated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    records_rejected: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    error_message: Mapped[str | None] = mapped_column(Text())
    run_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    category: Mapped[DataCategory | None] = relationship(back_populates="scraper_runs")
    source: Mapped[Source | None] = relationship(back_populates="scraper_runs")
    data_points: Mapped[list[DataPoint]] = relationship(back_populates="scraper_run")
    ingestion_logs: Mapped[list[IngestionLog]] = relationship(back_populates="scraper_run")


class IngestionLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "ingestion_logs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["data_point_id", "data_point_recorded_at"],
            ["data_points.id", "data_points.recorded_at"],
            ondelete="SET NULL",
        ),
        Index("ix_ingestion_logs_scraper_run_created_at", "scraper_run_id", "created_at"),
    )

    scraper_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("scraper_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_point_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    data_point_recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text(), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    scraper_run: Mapped[ScraperRun] = relationship(back_populates="ingestion_logs")
    data_point: Mapped[DataPoint | None] = relationship(back_populates="ingestion_logs")


from .data_point import DataPoint
from .reference import DataCategory, Source
