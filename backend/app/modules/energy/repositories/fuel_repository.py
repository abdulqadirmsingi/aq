"""Data access for normalized EWURA fuel observations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.data_point import DataPoint
from app.db.models.reference import Metric
from app.modules.energy.models.fuel import EnergyDetail

_EWURA_METRIC_SLUGS = (
    "ewura_petrol_cap_price",
    "ewura_diesel_cap_price",
    "ewura_kerosene_cap_price",
)


class FuelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_ewura_observations(
        self,
        *,
        limit: int,
        offset: int,
    ) -> list[DataPoint]:
        stmt = (
            select(DataPoint)
            .join(DataPoint.metric)
            .join(DataPoint.energy_detail)
            .where(Metric.slug.in_(_EWURA_METRIC_SLUGS))
            .where(EnergyDetail.energy_type == "fuel_cap_price")
            .where(DataPoint.is_current.is_(True))
            .options(
                joinedload(DataPoint.energy_detail),
                joinedload(DataPoint.location),
                joinedload(DataPoint.source),
                joinedload(DataPoint.metric),
            )
            .order_by(DataPoint.recorded_at.desc(), DataPoint.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
