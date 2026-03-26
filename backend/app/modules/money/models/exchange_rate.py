from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.data_point import DataPoint


class ExchangeRateDetail(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "exchange_rate_details"
    __table_args__ = (
        ForeignKeyConstraint(
            ["data_point_id", "data_point_recorded_at"],
            ["data_points.id", "data_points.recorded_at"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("data_point_id", "data_point_recorded_at"),
        Index(
            "ix_exchange_rate_details_lookup",
            "instrument_code",
            "quote_code",
            "rate_kind",
            "data_point_recorded_at",
        ),
        Index("ix_exchange_rate_details_market_channel", "market_scope", "channel"),
        Index(
            "ix_exchange_rate_details_source_effective_date",
            "source_effective_date",
        ),
        Index(
            "ix_exchange_rate_details_source_last_updated_at",
            "source_last_updated_at",
        ),
    )

    data_point_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    data_point_recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    instrument_code: Mapped[str] = mapped_column(String(16), nullable=False)
    instrument_name: Mapped[str | None] = mapped_column(String(120))
    instrument_type: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="currency",
        server_default="currency",
    )
    quote_code: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="TZS",
        server_default="TZS",
    )
    rate_kind: Mapped[str] = mapped_column(String(24), nullable=False)
    market_scope: Mapped[str] = mapped_column(String(32), nullable=False)
    channel: Mapped[str | None] = mapped_column(String(32))
    cash_note_band: Mapped[str | None] = mapped_column(String(32))
    source_effective_date: Mapped[date | None] = mapped_column(Date())
    source_last_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    inverse_rate: Mapped[float | None] = mapped_column(Numeric(24, 8))

    data_point: Mapped[DataPoint] = relationship(back_populates="exchange_rate_detail")
