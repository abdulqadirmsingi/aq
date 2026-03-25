"""API endpoints for normalized EWURA fuel data."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.energy.repositories.fuel_repository import FuelRepository
from app.modules.energy.schemas.fuel import (
    EwuraFuelAvailableMonthRead,
    EwuraFuelHistoryRead,
    EwuraFuelLatestPriceRead,
    EwuraFuelLatestSummaryRead,
    EwuraFuelMonthlyTrendRead,
    EwuraFuelObservationRead,
)
from app.modules.energy.services.fuel_service import FuelService

router = APIRouter(prefix="/energy", tags=["energy"])


def _fuel_service(db: AsyncSession) -> FuelService:
    return FuelService(FuelRepository(db))


@router.get(
    "/fuel/ewura/observations",
    response_model=list[EwuraFuelObservationRead],
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
) -> list[EwuraFuelObservationRead]:
    return await _fuel_service(db).list_ewura_observations(
        limit=limit,
        offset=offset,
        year=year,
        month=month,
        fuel_type=fuel_type,
        location_query=location_query,
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
    response_model=EwuraFuelHistoryRead,
    summary="Historical EWURA fuel observations",
)
async def get_ewura_fuel_history(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    fuel_type: Annotated[str | None, Query()] = None,
    location_id: Annotated[UUID | None, Query()] = None,
    location_query: Annotated[str | None, Query()] = None,
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    limit: Annotated[int, Query(ge=1, le=5000)] = 500,
) -> EwuraFuelHistoryRead:
    return await _fuel_service(db).get_history(
        fuel_type=fuel_type,
        location_id=location_id,
        location_query=location_query,
        year=year,
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
