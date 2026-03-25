"""Data access for fuel-related tables."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.energy.models.ewura_observation import EwuraFuelObservation


class FuelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_ewura_observations(
        self,
        *,
        limit: int,
        offset: int,
    ) -> list[EwuraFuelObservation]:
        stmt = (
            select(EwuraFuelObservation)
            .order_by(EwuraFuelObservation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
