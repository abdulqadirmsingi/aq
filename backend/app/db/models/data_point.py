from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Computed,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from .enums import MetricValueType


class DataPoint(Base):
    """Time-series facts; partitioned monthly on recorded_at (PostgreSQL)."""

    __tablename__ = "data_points"
    __table_args__ = (
        PrimaryKeyConstraint("id", "recorded_at"),
        ForeignKeyConstraint(
            ["supersedes_id", "supersedes_recorded_at"],
            ["data_points.id", "data_points.recorded_at"],
            ondelete="SET NULL",
        ),
        CheckConstraint(
            """
            (CASE WHEN value_numeric IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN value_text IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN value_boolean IS NOT NULL THEN 1 ELSE 0 END) <= 1
            """,
            name="single_scalar_value",
        ),
        CheckConstraint(
            """
            value_numeric IS NOT NULL OR
            value_text IS NOT NULL OR
            value_boolean IS NOT NULL OR
            extra_data <> '{}'::jsonb
            """,
            name="has_payload",
        ),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="confidence_score_range",
        ),
        CheckConstraint("version_no >= 1", name="version_no_positive"),
        Index("ix_data_points_metric_recorded_at", "metric_id", "recorded_at"),
        Index("ix_data_points_source_id", "source_id"),
        Index("ix_data_points_location_id", "location_id"),
        Index("ix_data_points_supersedes_id", "supersedes_id"),
        Index("ix_data_points_source_recorded_at", "source_id", "recorded_at"),
        Index(
            "ix_data_points_recorded_at_brin",
            "recorded_at",
            postgresql_using="brin",
        ),
        Index(
            "ix_data_points_current_metric_recorded_at",
            "metric_id",
            "recorded_at",
            postgresql_where=text("is_current"),
        ),
        Index(
            "uq_data_points_dedupe_key_current",
            "dedupe_key",
            "recorded_at",
            unique=True,
            postgresql_where=text("is_current"),
        ),
        {"postgresql_partition_by": "RANGE (recorded_at)"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    metric_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("metrics.id", ondelete="RESTRICT"),
        nullable=False,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="RESTRICT"),
        nullable=False,
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="SET NULL"),
    )
    scraper_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scraper_runs.id", ondelete="SET NULL"),
    )
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    supersedes_recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    external_reference: Mapped[str | None] = mapped_column(String(128))
    unit_override: Mapped[str | None] = mapped_column(String(32))
    value_type: Mapped[MetricValueType] = mapped_column(
        Enum(MetricValueType, name="metric_value_type_enum"),
        nullable=False,
        default=MetricValueType.NUMERIC,
        server_default=MetricValueType.NUMERIC.value,
    )
    value_numeric: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    value_text: Mapped[str | None] = mapped_column(Text())
    value_boolean: Mapped[bool | None] = mapped_column(Boolean)
    extra_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    ingestion_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    version_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        default=Decimal("1.0000"),
        server_default="1.0000",
    )
    dedupe_key: Mapped[str] = mapped_column(
        Text(),
        Computed(
            """
            md5(
                metric_id::text || '|' ||
                source_id::text || '|' ||
                coalesce(location_id::text, 'global') || '|' ||
                extract(
                    epoch from (
                        recorded_at - timestamptz '1970-01-01 00:00:00+00'
                    )
                )::text || '|' ||
                coalesce(external_reference, '')
            )
            """,
            persisted=True,
        ),
        nullable=False,
    )

    metric: Mapped[Metric] = relationship(back_populates="data_points")
    source: Mapped[Source] = relationship(back_populates="data_points")
    location: Mapped[Location | None] = relationship(back_populates="data_points")
    scraper_run: Mapped[ScraperRun | None] = relationship(back_populates="data_points")
    ingestion_logs: Mapped[list[IngestionLog]] = relationship(back_populates="data_point")
    energy_detail: Mapped[EnergyDetail | None] = relationship(back_populates="data_point")
    exchange_rate_detail: Mapped[ExchangeRateDetail | None] = relationship(
        back_populates="data_point"
    )
    salary_detail: Mapped[SalaryDetail | None] = relationship(back_populates="data_point")


from app.modules.energy.models.fuel import EnergyDetail
from app.modules.hr.models.salary import SalaryDetail
from app.modules.money.models.exchange_rate import ExchangeRateDetail

from .ingestion import IngestionLog, ScraperRun
from .reference import Location, Metric, Source
