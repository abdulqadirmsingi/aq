"""Pydantic response schemas for DSE stock market data."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DseStockRead(BaseModel):
    symbol: str
    exchange_code: str
    trade_date: date
    close_price: Decimal
    open_price: Decimal | None
    high_price: Decimal | None
    low_price: Decimal | None
    change_pct: Decimal | None
    turnover_tzs: Decimal | None

    model_config = {"from_attributes": True}


class DseDashboardSummaryRead(BaseModel):
    trade_date: date | None
    total_symbols: int
    total_turnover: Decimal
    top_gainer: DseStockRead | None
    top_loser: DseStockRead | None
    most_traded: DseStockRead | None
    gainers_count: int
    losers_count: int
    unchanged_count: int
