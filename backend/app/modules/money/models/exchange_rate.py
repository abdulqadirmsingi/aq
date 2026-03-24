from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ExchangeRateDetail(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "exchange_rate_details"
    __table_args__ = (
        Index("ix_exchange_rate_details_pair", "base_currency", "quote_currency"),
        Index("ix_exchange_rate_details_market", "market"),
    )

    data_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_points.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate_type: Mapped[str | None] = mapped_column(String(32))
    market: Mapped[str | None] = mapped_column(String(32))
    inverse_rate: Mapped[float | None] = mapped_column(Numeric(24, 8))

    data_point: Mapped[DataPoint] = relationship(back_populates="exchange_rate_detail")


from app.db.models.data_point import DataPoint
