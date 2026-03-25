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
    ExchangeRateBenchmarkGapSummaryRead,
    ExchangeRateBestRateSummaryRead,
    ExchangeRateLatestComparisonRead,
    ExchangeRateOpportunitySummaryRead,
    ExchangeRateRecommendationRead,
    ExchangeRateSpreadSummaryRead,
    ExchangeRateStalenessSummaryRead,
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


@router.get(
    "/exchange-rates/recommendation",
    response_model=ExchangeRateRecommendationRead,
)
async def get_exchange_rate_recommendation(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    instrument_code: Annotated[str, Query(min_length=1, max_length=16)],
    customer_action: Annotated[str, Query(pattern="^(buy|sell)$")],
    channel: Annotated[str | None, Query()] = None,
    cash_note_band: Annotated[str | None, Query()] = None,
    include_bot_as_option: Annotated[bool, Query()] = False,
) -> ExchangeRateRecommendationRead:
    return await _exchange_rate_service(db).get_recommendation(
        instrument_code=instrument_code,
        customer_action=customer_action,
        channel=channel,
        cash_note_band=cash_note_band,
        include_bot_as_option=include_bot_as_option,
    )


@router.get(
    "/exchange-rates/analytics/spreads",
    response_model=ExchangeRateSpreadSummaryRead,
)
async def get_exchange_rate_spreads(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    instrument_code: Annotated[str, Query(min_length=1, max_length=16)],
    channel: Annotated[str | None, Query()] = None,
    cash_note_band: Annotated[str | None, Query()] = None,
) -> ExchangeRateSpreadSummaryRead:
    return await _exchange_rate_service(db).get_spread_summary(
        instrument_code=instrument_code,
        channel=channel,
        cash_note_band=cash_note_band,
    )


@router.get(
    "/exchange-rates/analytics/benchmark-gaps",
    response_model=ExchangeRateBenchmarkGapSummaryRead,
)
async def get_exchange_rate_benchmark_gaps(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    instrument_code: Annotated[str, Query(min_length=1, max_length=16)],
    customer_action: Annotated[str, Query(pattern="^(buy|sell)$")],
    channel: Annotated[str | None, Query()] = None,
    cash_note_band: Annotated[str | None, Query()] = None,
) -> ExchangeRateBenchmarkGapSummaryRead:
    return await _exchange_rate_service(db).get_benchmark_gap_summary(
        instrument_code=instrument_code,
        customer_action=customer_action,
        channel=channel,
        cash_note_band=cash_note_band,
    )


@router.get(
    "/exchange-rates/analytics/staleness",
    response_model=ExchangeRateStalenessSummaryRead,
)
async def get_exchange_rate_staleness(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    instrument_code: Annotated[str, Query(min_length=1, max_length=16)],
    channel: Annotated[str | None, Query()] = None,
    cash_note_band: Annotated[str | None, Query()] = None,
) -> ExchangeRateStalenessSummaryRead:
    return await _exchange_rate_service(db).get_staleness_summary(
        instrument_code=instrument_code,
        channel=channel,
        cash_note_band=cash_note_band,
    )


@router.get(
    "/exchange-rates/analytics/best-rates",
    response_model=ExchangeRateBestRateSummaryRead,
)
async def get_exchange_rate_best_rates(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    instrument_code: Annotated[str, Query(min_length=1, max_length=16)],
    channel: Annotated[str | None, Query()] = None,
    cash_note_band: Annotated[str | None, Query()] = None,
) -> ExchangeRateBestRateSummaryRead:
    return await _exchange_rate_service(db).get_best_rate_summary(
        instrument_code=instrument_code,
        channel=channel,
        cash_note_band=cash_note_band,
    )


@router.get(
    "/exchange-rates/analytics/opportunities",
    response_model=ExchangeRateOpportunitySummaryRead,
)
async def get_exchange_rate_opportunities(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    instrument_code: Annotated[str, Query(min_length=1, max_length=16)],
    customer_action: Annotated[str, Query(pattern="^(buy|sell)$")],
    channel: Annotated[str | None, Query()] = None,
    cash_note_band: Annotated[str | None, Query()] = None,
) -> ExchangeRateOpportunitySummaryRead:
    return await _exchange_rate_service(db).get_opportunity_summary(
        instrument_code=instrument_code,
        customer_action=customer_action,
        channel=channel,
        cash_note_band=cash_note_band,
    )
