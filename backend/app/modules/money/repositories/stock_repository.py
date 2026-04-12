"""Read queries for DSE stock price data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.data_point import DataPoint
from app.db.models.reference import Metric, Source
from app.modules.money.models.stock import StockPriceDetail


@dataclass(frozen=True)
class StockRecord:
    symbol: str
    exchange_code: str
    trade_date: date
    close_price: Decimal
    open_price: Decimal | None
    high_price: Decimal | None
    low_price: Decimal | None
    change_pct: Decimal | None
    turnover_tzs: Decimal | None


_SOURCE_SLUG = "itrust_dse"
_METRIC_SLUG = "dse_close_price"


class StockRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _base_stmt(self):
        return (
            select(
                StockPriceDetail.symbol,
                StockPriceDetail.exchange_code,
                StockPriceDetail.trade_date,
                DataPoint.value_numeric.label("close_price"),
                StockPriceDetail.open_price,
                StockPriceDetail.high_price,
                StockPriceDetail.low_price,
                StockPriceDetail.change_pct,
                StockPriceDetail.turnover_tzs,
            )
            .join(
                DataPoint,
                (DataPoint.id == StockPriceDetail.data_point_id)
                & (DataPoint.recorded_at == StockPriceDetail.data_point_recorded_at),
            )
            .join(Metric, Metric.id == DataPoint.metric_id)
            .join(Source, Source.id == DataPoint.source_id)
            .where(
                Metric.slug == _METRIC_SLUG,
                Source.slug == _SOURCE_SLUG,
                DataPoint.is_current.is_(True),
            )
        )

    async def get_latest_trade_date(self) -> date | None:
        stmt = (
            select(func.max(cast(DataPoint.recorded_at, Date)))
            .join(Metric, Metric.id == DataPoint.metric_id)
            .join(Source, Source.id == DataPoint.source_id)
            .where(
                Metric.slug == _METRIC_SLUG,
                Source.slug == _SOURCE_SLUG,
                DataPoint.is_current.is_(True),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_latest(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        symbol: str | None = None,
    ) -> tuple[list[StockRecord], int]:
        latest_date = await self.get_latest_trade_date()
        if latest_date is None:
            return [], 0

        stmt = self._base_stmt().where(
            StockPriceDetail.trade_date == latest_date,
        )
        if symbol:
            stmt = stmt.where(StockPriceDetail.symbol == symbol.upper())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(
            StockPriceDetail.turnover_tzs.desc().nullslast(),
            StockPriceDetail.symbol,
        ).limit(limit).offset(offset)

        rows = (await self._session.execute(stmt)).mappings().all()
        return [StockRecord(**row) for row in rows], total

    async def list_history(
        self,
        symbol: str,
        *,
        limit: int = 30,
        offset: int = 0,
    ) -> tuple[list[StockRecord], int]:
        stmt = self._base_stmt().where(
            StockPriceDetail.symbol == symbol.upper(),
        )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(StockPriceDetail.trade_date.desc()).limit(limit).offset(offset)
        rows = (await self._session.execute(stmt)).mappings().all()
        return [StockRecord(**row) for row in rows], total

    async def get_dashboard_summary(self) -> dict:
        latest_date = await self.get_latest_trade_date()
        if latest_date is None:
            return {
                "trade_date": None,
                "total_symbols": 0,
                "total_turnover": Decimal("0"),
                "top_gainer": None,
                "top_loser": None,
                "most_traded": None,
                "gainers_count": 0,
                "losers_count": 0,
                "unchanged_count": 0,
            }

        all_records, total = await self.list_latest(limit=200, offset=0)

        top_gainer: StockRecord | None = None
        top_loser: StockRecord | None = None
        most_traded: StockRecord | None = None
        gainers = 0
        losers = 0
        unchanged = 0
        total_turnover = Decimal("0")

        for rec in all_records:
            if rec.turnover_tzs:
                total_turnover += rec.turnover_tzs

            if rec.change_pct is not None:
                if rec.change_pct > 0:
                    gainers += 1
                    if top_gainer is None or rec.change_pct > (top_gainer.change_pct or Decimal("0")):
                        top_gainer = rec
                elif rec.change_pct < 0:
                    losers += 1
                    if top_loser is None or rec.change_pct < (top_loser.change_pct or Decimal("0")):
                        top_loser = rec
                else:
                    unchanged += 1

            if rec.turnover_tzs and rec.turnover_tzs > 0:
                if most_traded is None or rec.turnover_tzs > (most_traded.turnover_tzs or Decimal("0")):
                    most_traded = rec

        return {
            "trade_date": latest_date,
            "total_symbols": total,
            "total_turnover": total_turnover,
            "top_gainer": top_gainer,
            "top_loser": top_loser,
            "most_traded": most_traded,
            "gainers_count": gainers,
            "losers_count": losers,
            "unchanged_count": unchanged,
        }
