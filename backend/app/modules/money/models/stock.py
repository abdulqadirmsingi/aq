"""SQLAlchemy model for stock_price_details."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
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


class StockPriceDetail(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "stock_price_details"
    __table_args__ = (
        ForeignKeyConstraint(
            ["data_point_id", "data_point_recorded_at"],
            ["data_points.id", "data_points.recorded_at"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("data_point_id", "data_point_recorded_at"),
        Index("ix_stock_price_details_symbol", "symbol"),
        Index("ix_stock_price_details_trade_date", "trade_date"),
        Index("ix_stock_price_details_symbol_trade_date", "symbol", "trade_date"),
    )

    data_point_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    data_point_recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    exchange_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="DSE",
        server_default="DSE",
    )
    open_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    high_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    low_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    change_pct: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    turnover_tzs: Mapped[Decimal | None] = mapped_column(Numeric(24, 4))
    trade_date: Mapped[date] = mapped_column(Date(), nullable=False)

    data_point: Mapped[DataPoint] = relationship(back_populates="stock_price_detail")
