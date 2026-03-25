"""API endpoints for fuel data."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.energy.repositories.fuel_repository import FuelRepository
from app.modules.energy.schemas.fuel import EwuraFuelObservationRead
from app.modules.energy.services.fuel_service import FuelService

router = APIRouter(prefix="/energy", tags=["energy"])


@router.get(
    "/fuel/ewura",
    response_model=list[EwuraFuelObservationRead],
    summary="List EWURA cap-price rows ingested by the scraper",
)
async def list_ewura_fuel_observations(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=5000)] = 200,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[EwuraFuelObservationRead]:
    repository = FuelRepository(db)
    service = FuelService(repository)
    return await service.list_ewura_observations(limit=limit, offset=offset)
