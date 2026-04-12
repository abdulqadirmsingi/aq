"""DSE stock market endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import Page
from app.db.session import get_db_session
from app.modules.money.repositories.stock_repository import StockRepository
from app.modules.money.schemas.stock import DseDashboardSummaryRead, DseStockRead
from app.modules.money.services.stock_service import StockService

router = APIRouter()


def _stock_service(db: AsyncSession) -> StockService:
    return StockService(StockRepository(db))


@router.get("/stocks/dse/latest", response_model=Page[DseStockRead])
async def get_latest_dse_stocks(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    symbol: Annotated[str | None, Query(max_length=20)] = None,
) -> Page[DseStockRead]:
    return await _stock_service(db).list_latest(
        limit=limit,
        offset=offset,
        symbol=symbol,
    )


@router.get("/stocks/dse/history", response_model=Page[DseStockRead])
async def get_dse_stock_history(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    symbol: Annotated[str, Query(min_length=1, max_length=20)],
    limit: Annotated[int, Query(ge=1, le=200)] = 30,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[DseStockRead]:
    return await _stock_service(db).list_history(
        symbol,
        limit=limit,
        offset=offset,
    )


@router.get("/stocks/dse/dashboard-summary", response_model=DseDashboardSummaryRead)
async def get_dse_dashboard_summary(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> DseDashboardSummaryRead:
    return await _stock_service(db).get_dashboard_summary()
