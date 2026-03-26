from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

from .enums import LocationLevel, MetricFrequency, MetricValueType, SourceType


class DataCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "data_categories"

    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    metrics: Mapped[list[Metric]] = relationship(back_populates="category")
    scraper_runs: Mapped[list[ScraperRun]] = relationship(back_populates="category")


class Source(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sources"
    __table_args__ = (
        CheckConstraint(
            "reliability_score >= 0 AND reliability_score <= 1",
            name="reliability_score_range",
        ),
    )

    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type_enum"),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text())
    url: Mapped[str | None] = mapped_column(String(255))
    reliability_score: Mapped[Decimal] = mapped_column(
        Numeric(4, 3),
        nullable=False,
        default=Decimal("0.500"),
        server_default="0.500",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    metrics: Mapped[list[Metric]] = relationship(back_populates="canonical_source")
    data_points: Mapped[list[DataPoint]] = relationship(back_populates="source")
    scraper_runs: Mapped[list[ScraperRun]] = relationship(back_populates="source")


class Metric(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "metrics"
    __table_args__ = (
        Index("ix_metrics_category_id", "category_id"),
        Index("uq_metrics_category_name", "category_id", "name", unique=True),
    )

    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(Text())
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    canonical_source_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"),
    )
    value_type: Mapped[MetricValueType] = mapped_column(
        Enum(MetricValueType, name="metric_value_type_enum"),
        nullable=False,
        default=MetricValueType.NUMERIC,
        server_default=MetricValueType.NUMERIC.value,
    )
    default_frequency: Mapped[MetricFrequency | None] = mapped_column(
        Enum(MetricFrequency, name="metric_frequency_enum"),
    )
    is_location_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    validation_rules: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    dimensions_schema: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    category: Mapped[DataCategory] = relationship(back_populates="metrics")
    canonical_source: Mapped[Source | None] = relationship(back_populates="metrics")
    data_points: Mapped[list[DataPoint]] = relationship(back_populates="metric")


class Location(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "locations"
    __table_args__ = (
        Index("ix_locations_parent_id", "parent_id"),
        Index(
            "uq_locations_parent_name_level",
            "parent_id",
            "name",
            "level",
            unique=True,
            postgresql_where=text("parent_id IS NOT NULL"),
        ),
        Index(
            "uq_locations_root_name_level",
            "name",
            "level",
            unique=True,
            postgresql_where=text("parent_id IS NULL"),
        ),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str | None] = mapped_column(String(32))
    level: Mapped[LocationLevel] = mapped_column(
        Enum(LocationLevel, name="location_level_enum"),
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
    )
    country_code: Mapped[str | None] = mapped_column(String(3))
    path: Mapped[str | None] = mapped_column(String(255), unique=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    parent: Mapped[Location | None] = relationship(
        remote_side="Location.id",
        back_populates="children",
    )
    children: Mapped[list[Location]] = relationship(back_populates="parent")
    data_points: Mapped[list[DataPoint]] = relationship(back_populates="location")


from .data_point import DataPoint
from .ingestion import ScraperRun
