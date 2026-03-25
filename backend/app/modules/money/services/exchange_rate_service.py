"""BOT exchange-rate read services."""

from __future__ import annotations

from datetime import date

from app.common.pagination import Page, build_page
from app.modules.money.repositories.exchange_rate_repository import (
    ExchangeRateRepository,
)
from app.modules.money.schemas.exchange_rate import (
    BotExchangeRateAvailableMonthRead,
    BotExchangeRateFiltersRead,
    BotExchangeRateRead,
    ExchangeRateComparisonRead,
    ExchangeRateLatestComparisonRead,
    ExchangeRateRecommendationCandidateRead,
    ExchangeRateRecommendationRead,
)


class ExchangeRateService:
    def __init__(self, repository: ExchangeRateRepository) -> None:
        self._repository = repository

    async def list_bot_latest(
        self,
        *,
        instrument_code: str | None,
        limit: int,
        offset: int,
    ) -> Page[BotExchangeRateRead]:
        snapshot_date = await self._repository.get_latest_bot_snapshot_date()
        if snapshot_date is None:
            return build_page([], total=0, limit=limit, offset=offset)
        rows = await self._repository.list_latest_bot_rates(
            snapshot_date=snapshot_date,
            instrument_code=instrument_code,
            limit=limit,
            offset=offset,
        )
        total = await self._repository.count_bot_rates(
            instrument_code=instrument_code,
            snapshot_date=snapshot_date,
        )
        return build_page(
            [self._to_read(row.snapshot_date, row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_bot_history(
        self,
        *,
        instrument_code: str | None,
        year: int | None,
        month: int | None,
        limit: int,
        offset: int,
    ) -> Page[BotExchangeRateRead]:
        rows = await self._repository.list_bot_history(
            instrument_code=instrument_code,
            year=year,
            month=month,
            limit=limit,
            offset=offset,
        )
        total = await self._repository.count_bot_rates(
            instrument_code=instrument_code,
            year=year,
            month=month,
        )
        return build_page(
            [self._to_read(row.snapshot_date, row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_bot_filters(self) -> BotExchangeRateFiltersRead:
        latest_snapshot_date = await self._repository.get_latest_bot_snapshot_date()
        available_months = await self._repository.list_bot_available_months()
        instrument_codes = await self._repository.list_bot_instruments()
        return BotExchangeRateFiltersRead(
            instrument_codes=instrument_codes,
            latest_snapshot_date=latest_snapshot_date,
            latest_snapshot_month_label=self._month_label(latest_snapshot_date),
            available_months=[
                BotExchangeRateAvailableMonthRead(
                    month_start=row.month_start,
                    month_label=self._month_label(row.month_start),
                    observation_count=row.observation_count,
                )
                for row in available_months
            ],
        )

    async def get_latest_comparison(
        self,
        *,
        instrument_code: str,
        channel: str | None = None,
        cash_note_band: str | None = None,
    ) -> ExchangeRateLatestComparisonRead:
        rows = await self._repository.list_latest_source_comparison(
            instrument_code=instrument_code,
            channel=channel,
            cash_note_band=cash_note_band,
        )
        return ExchangeRateLatestComparisonRead(
            instrument_code=instrument_code.upper(),
            channel=channel,
            cash_note_band=cash_note_band,
            items=[
                ExchangeRateComparisonRead(
                    source_slug=row.source_slug,
                    source_name=row.source_name,
                    snapshot_date=row.snapshot_date,
                    snapshot_month_label=self._month_label(row.snapshot_date) or "",
                    instrument_code=row.instrument_code,
                    instrument_name=row.instrument_name or row.instrument_code,
                    quote_code=row.quote_code,
                    buy_rate=row.buy_rate,
                    sell_rate=row.sell_rate,
                    mean_rate=row.mean_rate,
                    source_effective_date=row.source_effective_date,
                    source_last_updated_at=row.source_last_updated_at,
                    market_scope=row.market_scope,
                    channel=row.channel,
                    cash_note_band=row.cash_note_band,
                    created_at=row.created_at,
                )
                for row in rows
            ],
        )

    async def get_recommendation(
        self,
        *,
        instrument_code: str,
        customer_action: str,
        channel: str | None = None,
        cash_note_band: str | None = None,
        include_bot_as_option: bool = False,
    ) -> ExchangeRateRecommendationRead:
        rows = await self._repository.list_latest_source_comparison(
            instrument_code=instrument_code,
            channel=channel,
            cash_note_band=cash_note_band,
        )
        benchmark_row = next(
            (row for row in rows if row.source_slug == "bot_exchange_rates"),
            None,
        )
        if customer_action == "buy":
            rate_label = "sell_rate"
            relevant = [
                row
                for row in rows
                if row.sell_rate is not None
                and (include_bot_as_option or row.source_slug != "bot_exchange_rates")
            ]
            ordered = sorted(relevant, key=lambda row: row.sell_rate)
            best_rate = ordered[0].sell_rate if ordered else None
            bot_reference = (
                benchmark_row.mean_rate if benchmark_row is not None else None
            )
        else:
            rate_label = "buy_rate"
            relevant = [
                row
                for row in rows
                if row.buy_rate is not None
                and (include_bot_as_option or row.source_slug != "bot_exchange_rates")
            ]
            ordered = sorted(relevant, key=lambda row: row.buy_rate, reverse=True)
            best_rate = ordered[0].buy_rate if ordered else None
            bot_reference = (
                benchmark_row.mean_rate if benchmark_row is not None else None
            )

        candidates = [
            self._to_recommendation_candidate(
                row=row,
                customer_action=customer_action,
                rate_label=rate_label,
                rank=index,
                best_rate=best_rate,
                bot_reference=bot_reference,
            )
            for index, row in enumerate(ordered, start=1)
        ]
        return ExchangeRateRecommendationRead(
            instrument_code=instrument_code.upper(),
            customer_action=customer_action,
            channel=channel,
            cash_note_band=cash_note_band,
            best_option=candidates[0] if candidates else None,
            benchmark=(
                self._to_comparison_read(benchmark_row)
                if benchmark_row is not None
                else None
            ),
            compared_options=candidates,
        )

    def _to_read(self, snapshot_date: date, row) -> BotExchangeRateRead:
        return BotExchangeRateRead(
            snapshot_date=snapshot_date,
            snapshot_month_label=self._month_label(snapshot_date),
            instrument_code=row.instrument_code,
            instrument_name=row.instrument_name or row.instrument_code,
            quote_code=row.quote_code,
            buy_rate=row.buy_rate,
            sell_rate=row.sell_rate,
            mean_rate=row.mean_rate,
            source_effective_date=row.source_effective_date,
            source_last_updated_at=row.source_last_updated_at,
            market_scope="official_reference",
            created_at=row.created_at,
        )

    def _to_comparison_read(self, row) -> ExchangeRateComparisonRead:
        return ExchangeRateComparisonRead(
            source_slug=row.source_slug,
            source_name=row.source_name,
            snapshot_date=row.snapshot_date,
            snapshot_month_label=self._month_label(row.snapshot_date) or "",
            instrument_code=row.instrument_code,
            instrument_name=row.instrument_name or row.instrument_code,
            quote_code=row.quote_code,
            buy_rate=row.buy_rate,
            sell_rate=row.sell_rate,
            mean_rate=row.mean_rate,
            source_effective_date=row.source_effective_date,
            source_last_updated_at=row.source_last_updated_at,
            market_scope=row.market_scope,
            channel=row.channel,
            cash_note_band=row.cash_note_band,
            created_at=row.created_at,
        )

    def _to_recommendation_candidate(
        self,
        *,
        row,
        customer_action: str,
        rate_label: str,
        rank: int,
        best_rate,
        bot_reference,
    ) -> ExchangeRateRecommendationCandidateRead:
        relevant_rate = row.sell_rate if customer_action == "buy" else row.buy_rate
        difference_from_best = None
        if relevant_rate is not None and best_rate is not None:
            if customer_action == "buy":
                difference_from_best = relevant_rate - best_rate
            else:
                difference_from_best = best_rate - relevant_rate
        difference_from_bot_mean = None
        if relevant_rate is not None and bot_reference is not None:
            difference_from_bot_mean = relevant_rate - bot_reference
        return ExchangeRateRecommendationCandidateRead(
            source_slug=row.source_slug,
            source_name=row.source_name,
            snapshot_date=row.snapshot_date,
            snapshot_month_label=self._month_label(row.snapshot_date) or "",
            instrument_code=row.instrument_code,
            instrument_name=row.instrument_name or row.instrument_code,
            quote_code=row.quote_code,
            customer_action=customer_action,
            relevant_rate=relevant_rate,
            rate_label=rate_label,
            buy_rate=row.buy_rate,
            sell_rate=row.sell_rate,
            mean_rate=row.mean_rate,
            source_effective_date=row.source_effective_date,
            source_last_updated_at=row.source_last_updated_at,
            market_scope=row.market_scope,
            channel=row.channel,
            cash_note_band=row.cash_note_band,
            created_at=row.created_at,
            rank=rank,
            difference_from_best=difference_from_best,
            difference_from_bot_mean=difference_from_bot_mean,
        )

    def _month_label(self, value: date | None) -> str | None:
        return value.strftime("%B %Y") if value is not None else None
