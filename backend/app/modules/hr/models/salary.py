from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SalaryDetail(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "salary_details"
    __table_args__ = (
        Index("ix_salary_details_role_title", "role_title"),
        Index("ix_salary_details_seniority_level", "seniority_level"),
        Index("ix_salary_details_employment_type", "employment_type"),
    )

    data_point_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_points.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    role_title: Mapped[str | None] = mapped_column(String(120))
    seniority_level: Mapped[str | None] = mapped_column(String(32))
    employment_type: Mapped[str | None] = mapped_column(String(32))
    pay_period: Mapped[str | None] = mapped_column(String(16))
    currency_code: Mapped[str | None] = mapped_column(String(3))
    industry: Mapped[str | None] = mapped_column(String(64))

    data_point: Mapped[DataPoint] = relationship(back_populates="salary_detail")


from app.db.models.data_point import DataPoint
