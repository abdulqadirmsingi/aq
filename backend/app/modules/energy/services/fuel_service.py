"""Business logic for fuel data (EWURA cap prices)."""

from __future__ import annotations

from app.modules.energy.repositories.fuel_repository import FuelRepository
from app.modules.energy.schemas.fuel import EwuraFuelObservationRead


class FuelService:
    def __init__(self, repository: FuelRepository) -> None:
        self._repository = repository

    async def list_ewura_observations(
        self,
        *,
        limit: int,
        offset: int,
    ) -> list[EwuraFuelObservationRead]:
        rows = await self._repository.list_ewura_observations(
            limit=limit,
            offset=offset,
        )
        return [EwuraFuelObservationRead.model_validate(r) for r in rows]
