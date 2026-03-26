"""BOT exchange-rate read queries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.data_point import DataPoint
from app.db.models.reference import Metric, Source
from app.modules.money.models.exchange_rate import ExchangeRateDetail


@dataclass(frozen=True)
class BotExchangeRateRecord:
    snapshot_date: date
    instrument_code: str
    instrument_name: str | None
    quote_code: str
    buy_rate: Decimal | None
    sell_rate: Decimal | None
    mean_rate: Decimal | None
    source_effective_date: date | None
    source_last_updated_at: datetime | None
    created_at: datetime


@dataclass(frozen=True)
class BotExchangeRateMonthRecord:
    month_start: date
    observation_count: int


@dataclass(frozen=True)
class ExchangeRateComparisonRecord:
    source_slug: str
    source_name: str
    snapshot_date: date
    instrument_code: str
    instrument_name: str | None
    quote_code: str
    buy_rate: Decimal | None
    sell_rate: Decimal | None
    mean_rate: Decimal | None
    source_effective_date: date | None
    source_last_updated_at: datetime | None
    market_scope: str
    channel: str | None
    cash_note_band: str | None
    created_at: datetime


class ExchangeRateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _grouped_bot_rates_stmt(
        self,
        *,
        instrument_code: str | None = None,
        snapshot_date: date | None = None,
        year: int | None = None,
        month: int | None = None,
    ):
        stmt = (
            select(
                cast(DataPoint.recorded_at, Date).label("snapshot_date"),
                ExchangeRateDetail.instrument_code.label("instrument_code"),
                func.max(ExchangeRateDetail.instrument_name).label("instrument_name"),
                ExchangeRateDetail.quote_code.label("quote_code"),
                func.max(
                    case(
                        (Metric.slug == "fx_buy_rate", DataPoint.value_numeric),
                    )
                ).label("buy_rate"),
                func.max(
                    case(
                        (Metric.slug == "fx_sell_rate", DataPoint.value_numeric),
                    )
                ).label("sell_rate"),
                func.max(
                    case(
                        (Metric.slug == "fx_mean_rate", DataPoint.value_numeric),
                    )
                ).label("mean_rate"),
                func.max(ExchangeRateDetail.source_effective_date).label(
                    "source_effective_date"
                ),
                func.max(ExchangeRateDetail.source_last_updated_at).label(
                    "source_last_updated_at"
                ),
                func.max(DataPoint.created_at).label("created_at"),
            )
            .select_from(DataPoint)
            .join(Metric, DataPoint.metric_id == Metric.id)
            .join(Source, DataPoint.source_id == Source.id)
            .join(
                ExchangeRateDetail,
                (ExchangeRateDetail.data_point_id == DataPoint.id)
                & (ExchangeRateDetail.data_point_recorded_at == DataPoint.recorded_at),
            )
            .where(Source.slug == "bot_exchange_rates")
            .where(DataPoint.is_current.is_(True))
            .where(ExchangeRateDetail.market_scope == "official_reference")
            .group_by(
                cast(DataPoint.recorded_at, Date),
                ExchangeRateDetail.instrument_code,
                ExchangeRateDetail.quote_code,
            )
        )
        if instrument_code is not None:
            stmt = stmt.where(
                ExchangeRateDetail.instrument_code == instrument_code.upper()
            )
        if snapshot_date is not None:
            stmt = stmt.where(cast(DataPoint.recorded_at, Date) == snapshot_date)
        if year is not None:
            stmt = stmt.where(func.extract("year", DataPoint.recorded_at) == year)
        if month is not None:
            stmt = stmt.where(func.extract("month", DataPoint.recorded_at) == month)
        return stmt

    async def get_latest_bot_snapshot_date(self) -> date | None:
        stmt = (
            select(func.max(cast(DataPoint.recorded_at, Date)))
            .select_from(DataPoint)
            .join(Source, DataPoint.source_id == Source.id)
            .join(Metric, DataPoint.metric_id == Metric.id)
            .where(Source.slug == "bot_exchange_rates")
            .where(DataPoint.is_current.is_(True))
            .where(Metric.slug.in_(("fx_buy_rate", "fx_sell_rate", "fx_mean_rate")))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_latest_bot_rates(
        self,
        *,
        snapshot_date: date,
        instrument_code: str | None,
        limit: int,
        offset: int,
    ) -> list[BotExchangeRateRecord]:
        rows = await self._session.execute(
            self._grouped_bot_rates_stmt(
                instrument_code=instrument_code,
                snapshot_date=snapshot_date,
            )
            .order_by(ExchangeRateDetail.instrument_code.asc())
            .limit(limit)
            .offset(offset)
        )
        return [BotExchangeRateRecord(**row._mapping) for row in rows]

    async def count_bot_rates(
        self,
        *,
        instrument_code: str | None = None,
        snapshot_date: date | None = None,
        year: int | None = None,
        month: int | None = None,
    ) -> int:
        subquery = self._grouped_bot_rates_stmt(
            instrument_code=instrument_code,
            snapshot_date=snapshot_date,
            year=year,
            month=month,
        ).subquery()
        result = await self._session.execute(select(func.count()).select_from(subquery))
        return int(result.scalar_one())

    async def list_bot_history(
        self,
        *,
        instrument_code: str | None,
        year: int | None,
        month: int | None,
        limit: int,
        offset: int,
    ) -> list[BotExchangeRateRecord]:
        rows = await self._session.execute(
            self._grouped_bot_rates_stmt(
                instrument_code=instrument_code,
                year=year,
                month=month,
            )
            .order_by(
                cast(DataPoint.recorded_at, Date).desc(),
                ExchangeRateDetail.instrument_code.asc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return [BotExchangeRateRecord(**row._mapping) for row in rows]

    async def list_bot_available_months(self) -> list[BotExchangeRateMonthRecord]:
        month_start = cast(func.date_trunc("month", DataPoint.recorded_at), Date)
        rows = await self._session.execute(
            select(
                month_start.label("month_start"),
                func.count(
                    func.distinct(
                        func.concat(
                            ExchangeRateDetail.instrument_code,
                            "|",
                            cast(DataPoint.recorded_at, Date),
                        )
                    )
                ).label("observation_count"),
            )
            .select_from(DataPoint)
            .join(Source, DataPoint.source_id == Source.id)
            .join(
                ExchangeRateDetail,
                (ExchangeRateDetail.data_point_id == DataPoint.id)
                & (ExchangeRateDetail.data_point_recorded_at == DataPoint.recorded_at),
            )
            .where(Source.slug == "bot_exchange_rates")
            .where(DataPoint.is_current.is_(True))
            .group_by(month_start)
            .order_by(month_start.desc())
        )
        return [BotExchangeRateMonthRecord(**row._mapping) for row in rows]

    async def list_bot_instruments(self) -> list[str]:
        rows = await self._session.execute(
            select(ExchangeRateDetail.instrument_code)
            .select_from(DataPoint)
            .join(Source, DataPoint.source_id == Source.id)
            .join(
                ExchangeRateDetail,
                (ExchangeRateDetail.data_point_id == DataPoint.id)
                & (ExchangeRateDetail.data_point_recorded_at == DataPoint.recorded_at),
            )
            .where(Source.slug == "bot_exchange_rates")
            .where(DataPoint.is_current.is_(True))
            .distinct()
            .order_by(ExchangeRateDetail.instrument_code.asc())
        )
        return [row[0] for row in rows]

    async def list_latest_source_comparison(
        self,
        *,
        instrument_code: str,
        channel: str | None = None,
        cash_note_band: str | None = None,
        source_slugs: tuple[str, ...] = (
            "bot_exchange_rates",
            "crdb_forex",
            "nmb_daily_exchange_rates",
        ),
    ) -> list[ExchangeRateComparisonRecord]:
        records: list[ExchangeRateComparisonRecord] = []
        for source_slug in source_slugs:
            snapshot_date = await self._get_latest_snapshot_date_for_source(source_slug)
            if snapshot_date is None:
                continue
            rows = await self._session.execute(
                self._grouped_source_rates_stmt(
                    source_slug=source_slug,
                    instrument_code=instrument_code,
                    snapshot_date=snapshot_date,
                    channel=channel,
                    cash_note_band=cash_note_band,
                )
            )
            records.extend(
                ExchangeRateComparisonRecord(**row._mapping)
                for row in rows
            )
        return records

    async def _get_latest_snapshot_date_for_source(
        self,
        source_slug: str,
    ) -> date | None:
        stmt = (
            select(func.max(cast(DataPoint.recorded_at, Date)))
            .select_from(DataPoint)
            .join(Source, DataPoint.source_id == Source.id)
            .where(Source.slug == source_slug)
            .where(DataPoint.is_current.is_(True))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    def _grouped_source_rates_stmt(
        self,
        *,
        source_slug: str,
        instrument_code: str,
        snapshot_date: date,
        channel: str | None = None,
        cash_note_band: str | None = None,
    ):
        stmt = (
            select(
                Source.slug.label("source_slug"),
                Source.name.label("source_name"),
                cast(DataPoint.recorded_at, Date).label("snapshot_date"),
                ExchangeRateDetail.instrument_code.label("instrument_code"),
                func.max(ExchangeRateDetail.instrument_name).label("instrument_name"),
                ExchangeRateDetail.quote_code.label("quote_code"),
                func.max(
                    case((Metric.slug == "fx_buy_rate", DataPoint.value_numeric))
                ).label("buy_rate"),
                func.max(
                    case((Metric.slug == "fx_sell_rate", DataPoint.value_numeric))
                ).label("sell_rate"),
                func.max(
                    case((Metric.slug == "fx_mean_rate", DataPoint.value_numeric))
                ).label("mean_rate"),
                func.max(ExchangeRateDetail.source_effective_date).label(
                    "source_effective_date"
                ),
                func.max(ExchangeRateDetail.source_last_updated_at).label(
                    "source_last_updated_at"
                ),
                func.max(ExchangeRateDetail.market_scope).label("market_scope"),
                func.max(ExchangeRateDetail.channel).label("channel"),
                func.max(ExchangeRateDetail.cash_note_band).label("cash_note_band"),
                func.max(DataPoint.created_at).label("created_at"),
            )
            .select_from(DataPoint)
            .join(Metric, DataPoint.metric_id == Metric.id)
            .join(Source, DataPoint.source_id == Source.id)
            .join(
                ExchangeRateDetail,
                (ExchangeRateDetail.data_point_id == DataPoint.id)
                & (ExchangeRateDetail.data_point_recorded_at == DataPoint.recorded_at),
            )
            .where(Source.slug == source_slug)
            .where(DataPoint.is_current.is_(True))
            .where(ExchangeRateDetail.instrument_code == instrument_code.upper())
            .where(cast(DataPoint.recorded_at, Date) == snapshot_date)
            .group_by(
                Source.slug,
                Source.name,
                cast(DataPoint.recorded_at, Date),
                ExchangeRateDetail.instrument_code,
                ExchangeRateDetail.quote_code,
            )
            .order_by(Source.slug.asc())
        )
        if channel is not None:
            stmt = stmt.where(ExchangeRateDetail.channel == channel)
        if cash_note_band is not None:
            stmt = stmt.where(ExchangeRateDetail.cash_note_band == cash_note_band)
        return stmt
