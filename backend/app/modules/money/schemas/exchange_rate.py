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
