from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class ExchangeRateDetailPayload:
    instrument_code: str
    quote_code: str = "TZS"
    rate_kind: str = "buy"
    market_scope: str = "commercial_bank"
    instrument_name: str | None = None
    instrument_type: str = "currency"
    channel: str | None = None
    cash_note_band: str | None = None
    source_effective_date: date | None = None
    source_last_updated_at: datetime | None = None
    inverse_rate: Decimal | None = None


@dataclass(frozen=True)
class NormalizedFxObservation:
    source_slug: str
    metric_slug: str
    value: Decimal
    recorded_at: datetime
    external_reference: str
    detail: ExchangeRateDetailPayload
    location_path: str | None = None
    unit_override: str = "TZS"
    extra_data: dict[str, Any] = field(default_factory=dict)
    ingestion_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PersistObservationResult:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0

    def __add__(self, other: PersistObservationResult) -> PersistObservationResult:
        return PersistObservationResult(
            inserted=self.inserted + other.inserted,
            updated=self.updated + other.updated,
            skipped=self.skipped + other.skipped,
        )
