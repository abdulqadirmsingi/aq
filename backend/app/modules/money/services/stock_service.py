"""Business logic for DSE stock market data."""

from __future__ import annotations

from decimal import Decimal

from app.common.pagination import Page, build_page
from app.modules.money.repositories.stock_repository import StockRecord, StockRepository
from app.modules.money.schemas.stock import DseDashboardSummaryRead, DseStockRead, _fmt_turnover


def _to_schema(record: StockRecord) -> DseStockRead:
    return DseStockRead(
        symbol=record.symbol,
        exchange_code=record.exchange_code,
        trade_date=record.trade_date,
        close_price=float(record.close_price),
        open_price=float(record.open_price) if record.open_price is not None else None,
        high_price=float(record.high_price) if record.high_price is not None else None,
        low_price=float(record.low_price) if record.low_price is not None else None,
        change_pct=float(record.change_pct) if record.change_pct is not None else None,
        turnover_tzs=float(record.turnover_tzs) if record.turnover_tzs is not None else None,
    )


class StockService:
    def __init__(self, repository: StockRepository) -> None:
        self._repository = repository

    async def list_latest(
        self,
        *,
        limit: int = 20,
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
        total_turnover_dec = data["total_turnover"]
        return DseDashboardSummaryRead(
            trade_date=data["trade_date"],
            total_symbols=data["total_symbols"],
            total_turnover=float(total_turnover_dec),
            total_turnover_display=_fmt_turnover(
                total_turnover_dec if isinstance(total_turnover_dec, Decimal) else Decimal(str(total_turnover_dec))
            ),
            top_gainer=_to_schema(data["top_gainer"]) if data["top_gainer"] else None,
            top_loser=_to_schema(data["top_loser"]) if data["top_loser"] else None,
            most_traded=_to_schema(data["most_traded"]) if data["most_traded"] else None,
            gainers_count=data["gainers_count"],
            losers_count=data["losers_count"],
            unchanged_count=data["unchanged_count"],
        )
