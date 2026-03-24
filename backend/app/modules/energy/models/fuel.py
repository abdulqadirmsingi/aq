from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class EnergyDetail(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "energy_details"
    __table_args__ = (
        Index("ix_energy_details_energy_type", "energy_type"),
        Index("ix_energy_details_fuel_grade", "fuel_grade"),
        Index("ix_energy_details_tariff_code", "tariff_code"),
    )

    data_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_points.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    energy_type: Mapped[str] = mapped_column(String(32), nullable=False)
    fuel_grade: Mapped[str | None] = mapped_column(String(32))
    tariff_code: Mapped[str | None] = mapped_column(String(32))
    customer_type: Mapped[str | None] = mapped_column(String(32))
    provider_name: Mapped[str | None] = mapped_column(String(120))

    data_point: Mapped[DataPoint] = relationship(back_populates="energy_detail")


from app.db.models.data_point import DataPoint
