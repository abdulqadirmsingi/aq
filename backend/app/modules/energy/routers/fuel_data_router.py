"""Primary EWURA fuel data endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import Page
from app.db.session import get_db_session
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
from app.modules.energy.services.fuel_service import FuelService

router = APIRouter()


def _fuel_service(db: AsyncSession) -> FuelService:
    return FuelService(FuelRepository(db))


@router.get("/fuel/ewura/observations", response_model=Page[EwuraFuelObservationRead])
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


@router.get("/fuel/ewura/latest", response_model=list[EwuraFuelLatestPriceRead])
async def get_latest_ewura_fuel_prices(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    fuel_type: Annotated[str | None, Query()] = None,
    location_query: Annotated[str | None, Query()] = None,
) -> list[EwuraFuelLatestPriceRead]:
    return await _fuel_service(db).get_latest_prices(
        fuel_type=fuel_type,
        location_query=location_query,
    )


@router.get("/fuel/ewura/latest-summary", response_model=EwuraFuelLatestSummaryRead | None)
async def get_latest_ewura_fuel_summary(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> EwuraFuelLatestSummaryRead | None:
    return await _fuel_service(db).get_latest_summary()


@router.get("/fuel/ewura/current-year", response_model=list[EwuraFuelMonthlyTrendRead])
async def get_current_year_ewura_fuel_trends(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    fuel_type: Annotated[str | None, Query()] = None,
) -> list[EwuraFuelMonthlyTrendRead]:
    return await _fuel_service(db).get_current_year_trends(
        year=year,
        fuel_type=fuel_type,
    )


@router.get("/fuel/ewura/history", response_model=Page[EwuraFuelObservationRead])
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


@router.get("/fuel/ewura/available-months", response_model=list[EwuraFuelAvailableMonthRead])
async def get_ewura_available_months(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[EwuraFuelAvailableMonthRead]:
    return await _fuel_service(db).get_available_months()


@router.get("/fuel/ewura/dashboard-summary", response_model=EwuraFuelDashboardSummaryRead)
async def get_ewura_dashboard_summary(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> EwuraFuelDashboardSummaryRead:
    return await _fuel_service(db).get_dashboard_summary()


@router.get("/fuel/ewura/rollups", response_model=list[EwuraFuelRollupRead])
async def get_ewura_rollups(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    level: Annotated[str, Query(pattern="^(city|region)$")] = "city",
    fuel_type: Annotated[str | None, Query()] = None,
) -> list[EwuraFuelRollupRead]:
    return await _fuel_service(db).get_rollups(level=level, fuel_type=fuel_type)


@router.get("/fuel/ewura/latest-extremes", response_model=EwuraFuelLatestExtremesRead | None)
async def get_ewura_latest_extremes(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    fuel_type: Annotated[str | None, Query()] = None,
    top: Annotated[int, Query(ge=1, le=50)] = 10,
) -> EwuraFuelLatestExtremesRead | None:
    return await _fuel_service(db).get_latest_extremes(fuel_type=fuel_type, top=top)


@router.get("/fuel/ewura/insights", response_model=list[EwuraFuelInsightRead])
async def get_ewura_insights(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[EwuraFuelInsightRead]:
    return await _fuel_service(db).get_insights()
