"""EWURA scraper monitoring endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import Page
from app.db.session import get_db_session
from app.modules.energy.repositories.fuel_monitor_repository import (
    FuelMonitorRepository,
)
from app.modules.energy.schemas.fuel_monitor import (
    EwuraFuelRunLogRead,
    EwuraFuelRunRead,
)
from app.modules.energy.services.fuel_monitor_service import FuelMonitorService

router = APIRouter()


def _fuel_monitor_service(db: AsyncSession) -> FuelMonitorService:
    return FuelMonitorService(FuelMonitorRepository(db))


@router.get("/fuel/ewura/runs", response_model=Page[EwuraFuelRunRead])
async def list_ewura_scraper_runs(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    status: Annotated[str | None, Query()] = None,
) -> Page[EwuraFuelRunRead]:
    return await _fuel_monitor_service(db).list_runs(
        limit=limit,
        offset=offset,
        status=status,
    )


@router.get("/fuel/ewura/runs/{run_id}", response_model=EwuraFuelRunRead | None)
async def get_ewura_scraper_run(
    run_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> EwuraFuelRunRead | None:
    return await _fuel_monitor_service(db).get_run(run_id)


@router.get("/fuel/ewura/runs/{run_id}/logs", response_model=Page[EwuraFuelRunLogRead])
async def list_ewura_scraper_run_logs(
    run_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    level: Annotated[str | None, Query()] = None,
    event_type: Annotated[str | None, Query()] = None,
) -> Page[EwuraFuelRunLogRead]:
    return await _fuel_monitor_service(db).list_run_logs(
        run_id=run_id,
        limit=limit,
        offset=offset,
        level=level,
        event_type=event_type,
    )
