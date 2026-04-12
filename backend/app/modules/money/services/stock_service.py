"""Business logic for DSE stock market data."""

from __future__ import annotations

from app.common.pagination import Page, build_page
from app.modules.money.repositories.stock_repository import StockRepository
from app.modules.money.schemas.stock import DseDashboardSummaryRead, DseStockRead


def _to_schema(record) -> DseStockRead:
    return DseStockRead(
        symbol=record.symbol,
        exchange_code=record.exchange_code,
        trade_date=record.trade_date,
        close_price=record.close_price,
        open_price=record.open_price,
        high_price=record.high_price,
        low_price=record.low_price,
        change_pct=record.change_pct,
        turnover_tzs=record.turnover_tzs,
    )


class StockService:
    def __init__(self, repository: StockRepository) -> None:
        self._repository = repository

    async def list_latest(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        symbol: str | None = None,
    ) -> Page[DseStockRead]:
        records, total = await self._repository.list_latest(
            limit=limit,
            offset=offset,
            symbol=symbol,
        )
        return build_page(
            [_to_schema(r) for r in records],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_history(
        self,
        symbol: str,
        *,
        limit: int = 30,
        offset: int = 0,
    ) -> Page[DseStockRead]:
        records, total = await self._repository.list_history(
            symbol,
            limit=limit,
            offset=offset,
        )
        return build_page(
            [_to_schema(r) for r in records],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_dashboard_summary(self) -> DseDashboardSummaryRead:
        data = await self._repository.get_dashboard_summary()
        return DseDashboardSummaryRead(
            trade_date=data["trade_date"],
            total_symbols=data["total_symbols"],
            total_turnover=data["total_turnover"],
            top_gainer=_to_schema(data["top_gainer"]) if data["top_gainer"] else None,
            top_loser=_to_schema(data["top_loser"]) if data["top_loser"] else None,
            most_traded=_to_schema(data["most_traded"]) if data["most_traded"] else None,
            gainers_count=data["gainers_count"],
            losers_count=data["losers_count"],
            unchanged_count=data["unchanged_count"],
        )
