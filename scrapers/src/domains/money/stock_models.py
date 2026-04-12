"""Pydantic/dataclass models for DSE stock price scraper payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class StockPriceDetailPayload:
    symbol: str
    trade_date: date
    exchange_code: str = "DSE"
    open_price: Decimal | None = None
    high_price: Decimal | None = None
    low_price: Decimal | None = None
    change_pct: Decimal | None = None
    turnover_tzs: Decimal | None = None


@dataclass(frozen=True)
class NormalizedStockObservation:
    """One closing-price observation for one DSE symbol on one trade date."""

    source_slug: str
    metric_slug: str
    value: Decimal  # close price
    recorded_at: datetime
    external_reference: str  # "{SYMBOL}|{TRADE_DATE}"
    detail: StockPriceDetailPayload
    location_path: str = "TZ"
    unit_override: str = "TZS"
    extra_data: dict[str, Any] = field(default_factory=dict)
    ingestion_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PersistStockResult:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0

    def __add__(self, other: PersistStockResult) -> PersistStockResult:
        return PersistStockResult(
            inserted=self.inserted + other.inserted,
            updated=self.updated + other.updated,
            skipped=self.skipped + other.skipped,
        )
