"""Procurement domain data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class NormalizedTender:
    ocid: str
    tender_reference: str
    title: str
    description: str | None
    procuring_entity_name: str | None
    procuring_entity_id: str | None
    procurement_method: str | None
    procurement_method_details: str | None
    tender_status: str | None
    tender_value_amount: Decimal | None
    tender_value_currency: str | None
    tender_period_start: datetime | None
    tender_period_end: datetime | None
    has_award: bool
    award_date: datetime | None
    award_value_amount: Decimal | None
    award_value_currency: str | None
    contractor_name: str | None
    contractor_id: str | None
    financial_year: str | None
    location: str | None
    raw_ocds: dict[str, Any]
    source_url: str | None
    raw_ocds_fingerprint: str


@dataclass
class PersistResult:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0

    def __add__(self, other: PersistResult) -> PersistResult:
        return PersistResult(
            inserted=self.inserted + other.inserted,
            updated=self.updated + other.updated,
            skipped=self.skipped + other.skipped,
        )
