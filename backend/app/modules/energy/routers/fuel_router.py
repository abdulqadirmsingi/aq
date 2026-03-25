"""API endpoints for normalized EWURA fuel data."""

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
from app.modules.energy.repositories.fuel_repository import FuelRepository
from app.modules.energy.schemas.fuel import (
    EwuraFuelAvailableMonthRead,
    EwuraFuelDashboardSummaryRead,
    EwuraFuelInsightRead,
    EwuraFuelLatestExtremesRead,
    EwuraFuelLatestPriceRead,
    EwuraFuelLatestSummaryRead,
    EwuraFuelMonthlyTrendRead,
    EwuraFuelObservationRead,
    EwuraFuelRollupRead,
)
from app.modules.energy.schemas.fuel_monitor import (
    EwuraFuelRunLogRead,
    EwuraFuelRunRead,
)
from app.modules.energy.services.fuel_monitor_service import FuelMonitorService
from app.modules.energy.services.fuel_service import FuelService

router = APIRouter(prefix="/energy", tags=["energy"])


def _fuel_service(db: AsyncSession) -> FuelService:
    return FuelService(FuelRepository(db))


def _fuel_monitor_service(db: AsyncSession) -> FuelMonitorService:
    return FuelMonitorService(FuelMonitorRepository(db))


@router.get(
    "/fuel/ewura/observations",
    response_model=Page[EwuraFuelObservationRead],
    summary="List normalized EWURA fuel observations",
)
async def list_ewura_fuel_observations(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=5000)] = 200,
    offset: Annotated[int, Query(ge=0)] = 0,
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    fuel_type: Annotated[str | None, Query()] = None,
    location_query: Annotated[str | None, Query()] = None,
    location_id: Annotated[UUID | None, Query()] = None,
) -> Page[EwuraFuelObservationRead]:
    return await _fuel_service(db).list_ewura_observations(
        limit=limit,
        offset=offset,
        year=year,
        month=month,
        fuel_type=fuel_type,
        location_query=location_query,
        location_id=location_id,
    )


@router.get(
    "/fuel/ewura/latest",
    response_model=list[EwuraFuelLatestPriceRead],
    summary="Latest available EWURA fuel prices with previous comparison",
)
async def get_latest_ewura_fuel_prices(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    fuel_type: Annotated[str | None, Query()] = None,
    location_query: Annotated[str | None, Query()] = None,
) -> list[EwuraFuelLatestPriceRead]:
    return await _fuel_service(db).get_latest_prices(
        fuel_type=fuel_type,
        location_query=location_query,
    )


@router.get(
    "/fuel/ewura/latest-summary",
    response_model=EwuraFuelLatestSummaryRead | None,
    summary="Latest available EWURA month summary by fuel type",
)
async def get_latest_ewura_fuel_summary(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> EwuraFuelLatestSummaryRead | None:
    return await _fuel_service(db).get_latest_summary()


@router.get(
    "/fuel/ewura/current-year",
    response_model=list[EwuraFuelMonthlyTrendRead],
    summary="Current year EWURA monthly fuel trends",
)
async def get_current_year_ewura_fuel_trends(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    fuel_type: Annotated[str | None, Query()] = None,
) -> list[EwuraFuelMonthlyTrendRead]:
    return await _fuel_service(db).get_current_year_trends(
        year=year,
        fuel_type=fuel_type,
    )


@router.get(
    "/fuel/ewura/history",
    response_model=Page[EwuraFuelObservationRead],
    summary="Historical EWURA fuel observations",
)
async def get_ewura_fuel_history(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    fuel_type: Annotated[str | None, Query()] = None,
    location_id: Annotated[UUID | None, Query()] = None,
    location_query: Annotated[str | None, Query()] = None,
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=5000)] = 500,
) -> Page[EwuraFuelObservationRead]:
    return await _fuel_service(db).get_history(
        fuel_type=fuel_type,
        location_id=location_id,
        location_query=location_query,
        year=year,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/fuel/ewura/available-months",
    response_model=list[EwuraFuelAvailableMonthRead],
    summary="Available EWURA months in the dataset",
)
async def get_ewura_available_months(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[EwuraFuelAvailableMonthRead]:
    return await _fuel_service(db).get_available_months()


@router.get(
    "/fuel/ewura/dashboard-summary",
    response_model=EwuraFuelDashboardSummaryRead,
    summary="Backend-ready EWURA dashboard summary payload",
)
async def get_ewura_dashboard_summary(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> EwuraFuelDashboardSummaryRead:
    return await _fuel_service(db).get_dashboard_summary()


@router.get(
    "/fuel/ewura/rollups",
    response_model=list[EwuraFuelRollupRead],
    summary="Latest EWURA price rollups by city or region",
)
async def get_ewura_rollups(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    level: Annotated[str, Query(pattern="^(city|region)$")] = "city",
    fuel_type: Annotated[str | None, Query()] = None,
) -> list[EwuraFuelRollupRead]:
    return await _fuel_service(db).get_rollups(level=level, fuel_type=fuel_type)


@router.get(
    "/fuel/ewura/latest-extremes",
    response_model=EwuraFuelLatestExtremesRead | None,
    summary="Cheapest and most expensive latest EWURA prices",
)
async def get_ewura_latest_extremes(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    fuel_type: Annotated[str | None, Query()] = None,
    top: Annotated[int, Query(ge=1, le=50)] = 10,
) -> EwuraFuelLatestExtremesRead | None:
    return await _fuel_service(db).get_latest_extremes(fuel_type=fuel_type, top=top)


@router.get(
    "/fuel/ewura/insights",
    response_model=list[EwuraFuelInsightRead],
    summary="Month-over-month backend-generated EWURA insights",
)
async def get_ewura_insights(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[EwuraFuelInsightRead]:
    return await _fuel_service(db).get_insights()


@router.get(
    "/fuel/ewura/runs",
    response_model=Page[EwuraFuelRunRead],
    summary="Paginated EWURA scraper runs",
)
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


@router.get(
    "/fuel/ewura/runs/{run_id}",
    response_model=EwuraFuelRunRead | None,
    summary="Get one EWURA scraper run",
)
async def get_ewura_scraper_run(
    run_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> EwuraFuelRunRead | None:
    return await _fuel_monitor_service(db).get_run(run_id)


@router.get(
    "/fuel/ewura/runs/{run_id}/logs",
    response_model=Page[EwuraFuelRunLogRead],
    summary="Paginated ingestion logs for one EWURA scraper run",
)
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
