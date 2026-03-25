"""BOT exchange-rate endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import Page
from app.db.session import get_db_session
from app.modules.money.repositories.exchange_rate_repository import (
    ExchangeRateRepository,
)
from app.modules.money.schemas.exchange_rate import (
    BotExchangeRateFiltersRead,
    BotExchangeRateRead,
    ExchangeRateLatestComparisonRead,
)
from app.modules.money.services.exchange_rate_service import ExchangeRateService

router = APIRouter()


def _exchange_rate_service(db: AsyncSession) -> ExchangeRateService:
    return ExchangeRateService(ExchangeRateRepository(db))


@router.get("/exchange-rates/bot/latest", response_model=Page[BotExchangeRateRead])
async def get_latest_bot_exchange_rates(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=5000)] = 200,
    offset: Annotated[int, Query(ge=0)] = 0,
    instrument_code: Annotated[str | None, Query()] = None,
) -> Page[BotExchangeRateRead]:
    return await _exchange_rate_service(db).list_bot_latest(
        instrument_code=instrument_code,
        limit=limit,
        offset=offset,
    )


@router.get("/exchange-rates/bot/history", response_model=Page[BotExchangeRateRead])
async def get_bot_exchange_rate_history(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=5000)] = 200,
    offset: Annotated[int, Query(ge=0)] = 0,
    instrument_code: Annotated[str | None, Query()] = None,
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
) -> Page[BotExchangeRateRead]:
    return await _exchange_rate_service(db).list_bot_history(
        instrument_code=instrument_code,
        year=year,
        month=month,
        limit=limit,
        offset=offset,
    )


@router.get("/exchange-rates/bot/filters", response_model=BotExchangeRateFiltersRead)
async def get_bot_exchange_rate_filters(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> BotExchangeRateFiltersRead:
    return await _exchange_rate_service(db).get_bot_filters()


@router.get(
    "/exchange-rates/latest-comparison",
    response_model=ExchangeRateLatestComparisonRead,
)
async def get_latest_exchange_rate_comparison(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    instrument_code: Annotated[str, Query(min_length=1, max_length=16)],
    channel: Annotated[str | None, Query()] = None,
    cash_note_band: Annotated[str | None, Query()] = None,
) -> ExchangeRateLatestComparisonRead:
    return await _exchange_rate_service(db).get_latest_comparison(
        instrument_code=instrument_code,
        channel=channel,
        cash_note_band=cash_note_band,
    )
