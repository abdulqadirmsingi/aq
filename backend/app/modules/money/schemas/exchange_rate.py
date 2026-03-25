"""Pydantic schemas for BOT exchange-rate responses."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class BotExchangeRateRead(BaseModel):
    snapshot_date: date
    snapshot_month_label: str
    instrument_code: str
    instrument_name: str
    quote_code: str
    buy_rate: Decimal | None
    sell_rate: Decimal | None
    mean_rate: Decimal | None
    source_effective_date: date | None
    source_last_updated_at: datetime | None
    market_scope: str
    created_at: datetime


class BotExchangeRateAvailableMonthRead(BaseModel):
    month_start: date
    month_label: str | None
    observation_count: int


class BotExchangeRateFiltersRead(BaseModel):
    instrument_codes: list[str]
    latest_snapshot_date: date | None
    latest_snapshot_month_label: str | None
    available_months: list[BotExchangeRateAvailableMonthRead]


class ExchangeRateComparisonRead(BaseModel):
    source_slug: str
    source_name: str
    snapshot_date: date
    snapshot_month_label: str
    instrument_code: str
    instrument_name: str
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


class ExchangeRateLatestComparisonRead(BaseModel):
    instrument_code: str
    channel: str | None = None
    cash_note_band: str | None = None
    items: list[ExchangeRateComparisonRead]


class ExchangeRateRecommendationCandidateRead(BaseModel):
    source_slug: str
    source_name: str
    snapshot_date: date
    snapshot_month_label: str
    instrument_code: str
    instrument_name: str
    quote_code: str
    customer_action: str
    relevant_rate: Decimal
    rate_label: str
    buy_rate: Decimal | None
    sell_rate: Decimal | None
    mean_rate: Decimal | None
    source_effective_date: date | None
    source_last_updated_at: datetime | None
    market_scope: str
    channel: str | None
    cash_note_band: str | None
    created_at: datetime
    rank: int
    difference_from_best: Decimal | None
    difference_from_bot_mean: Decimal | None


class ExchangeRateRecommendationRead(BaseModel):
    instrument_code: str
    customer_action: str
    channel: str | None = None
    cash_note_band: str | None = None
    best_option: ExchangeRateRecommendationCandidateRead | None
    benchmark: ExchangeRateComparisonRead | None
    compared_options: list[ExchangeRateRecommendationCandidateRead]


class ExchangeRateSpreadRead(BaseModel):
    source_slug: str
    source_name: str
    snapshot_date: date
    snapshot_month_label: str
    instrument_code: str
    instrument_name: str
    buy_rate: Decimal
    sell_rate: Decimal
    spread: Decimal
    spread_percent_of_buy: Decimal | None
    market_scope: str
    channel: str | None
    cash_note_band: str | None
    source_last_updated_at: datetime | None


class ExchangeRateSpreadSummaryRead(BaseModel):
    instrument_code: str
    channel: str | None = None
    cash_note_band: str | None = None
    items: list[ExchangeRateSpreadRead]


class ExchangeRateBenchmarkGapRead(BaseModel):
    source_slug: str
    source_name: str
    snapshot_date: date
    snapshot_month_label: str
    instrument_code: str
    instrument_name: str
    comparison_basis: str
    relevant_rate: Decimal
    bot_mean_rate: Decimal
    absolute_gap: Decimal
    percent_gap: Decimal | None
    market_scope: str
    channel: str | None
    cash_note_band: str | None


class ExchangeRateBenchmarkGapSummaryRead(BaseModel):
    instrument_code: str
    customer_action: str
    channel: str | None = None
    cash_note_band: str | None = None
    bot_mean_rate: Decimal | None
    items: list[ExchangeRateBenchmarkGapRead]


class ExchangeRateStalenessRead(BaseModel):
    source_slug: str
    source_name: str
    instrument_code: str
    snapshot_date: date
    source_effective_date: date | None
    source_last_updated_at: datetime | None
    data_timestamp: datetime
    lag_hours_vs_freshest: Decimal
    is_freshest: bool
    market_scope: str
    channel: str | None
    cash_note_band: str | None


class ExchangeRateStalenessSummaryRead(BaseModel):
    instrument_code: str
    channel: str | None = None
    cash_note_band: str | None = None
    freshest_timestamp: datetime | None
    items: list[ExchangeRateStalenessRead]


class ExchangeRateBestRateRead(BaseModel):
    customer_action: str
    best_option: ExchangeRateRecommendationCandidateRead | None
    benchmark: ExchangeRateComparisonRead | None


class ExchangeRateBestRateSummaryRead(BaseModel):
    instrument_code: str
    channel: str | None = None
    cash_note_band: str | None = None
    buy_forex: ExchangeRateBestRateRead
    sell_forex: ExchangeRateBestRateRead


class ExchangeRateOpportunityRead(BaseModel):
    customer_action: str
    best_source_slug: str
    best_source_name: str
    compared_source_slug: str
    compared_source_name: str
    instrument_code: str
    relevant_rate: Decimal
    best_rate: Decimal
    absolute_difference: Decimal
    percent_difference: Decimal | None
    channel: str | None
    cash_note_band: str | None


class ExchangeRateOpportunitySummaryRead(BaseModel):
    instrument_code: str
    customer_action: str
    channel: str | None = None
    cash_note_band: str | None = None
    best_source_slug: str | None
    opportunities: list[ExchangeRateOpportunityRead]
