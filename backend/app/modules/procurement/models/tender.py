from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ProcurementTender(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One row per OCID — the compiled view of a Tanzania government tender."""

    __tablename__ = "procurement_tenders"
    __table_args__ = (
        Index("ix_procurement_tenders_ocid", "ocid", unique=True),
        Index("ix_procurement_tenders_tender_status", "tender_status"),
        Index("ix_procurement_tenders_has_award", "has_award"),
        Index("ix_procurement_tenders_procurement_method", "procurement_method"),
        Index("ix_procurement_tenders_procuring_entity_id", "procuring_entity_id"),
        Index("ix_procurement_tenders_tender_period_end", "tender_period_end"),
        Index("ix_procurement_tenders_award_date", "award_date"),
        Index("ix_procurement_tenders_financial_year", "financial_year"),
        Index("ix_procurement_tenders_raw_ocds_gin", "raw_ocds", postgresql_using="gin"),
    )

    ocid: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    tender_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(Text(), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    procuring_entity_name: Mapped[str | None] = mapped_column(String(500))
    procuring_entity_id: Mapped[str | None] = mapped_column(String(255))
    procurement_method: Mapped[str | None] = mapped_column(String(64))
    procurement_method_details: Mapped[str | None] = mapped_column(String(255))
    tender_status: Mapped[str | None] = mapped_column(String(64))
    tender_value_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    tender_value_currency: Mapped[str | None] = mapped_column(String(8))
    tender_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    tender_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    has_award: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    award_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    award_value_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    award_value_currency: Mapped[str | None] = mapped_column(String(8))
    contractor_name: Mapped[str | None] = mapped_column(String(500))
    contractor_id: Mapped[str | None] = mapped_column(String(255))
    financial_year: Mapped[str | None] = mapped_column(String(16))
    location: Mapped[str | None] = mapped_column(Text())
    raw_ocds: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    raw_ocds_fingerprint: Mapped[str] = mapped_column(String(32), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
