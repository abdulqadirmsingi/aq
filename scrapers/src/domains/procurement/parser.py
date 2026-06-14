"""Parse raw OCDS record JSON into NormalizedTender instances."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from src.domains.procurement.models import NormalizedTender

logger = logging.getLogger(__name__)

_DATETIME_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
)


def parse_ocds_record(
    record: dict[str, Any],
    *,
    source_url: str | None = None,
) -> NormalizedTender | None:
    """Parse one OCDS record. Returns None and logs a warning on failure."""
    ocid = record.get("ocid", "unknown")
    try:
        return _parse(record, source_url=source_url)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Skipping unparseable OCDS record %s: %s", ocid, exc)
        return None


def _parse(record: dict[str, Any], *, source_url: str | None) -> NormalizedTender:
    # compiledRelease is the full merged view; fall back to the record itself
    compiled = record.get("compiledRelease") or record
    ocid = record.get("ocid") or compiled.get("ocid") or ""

    tender: dict[str, Any] = compiled.get("tender") or {}
    buyer: dict[str, Any] = compiled.get("buyer") or {}
    awards: list[dict[str, Any]] = compiled.get("awards") or []

    active_awards = [a for a in awards if a.get("status") == "active"]
    primary_award = active_awards[0] if active_awards else (awards[0] if awards else None)

    suppliers: list[dict[str, Any]] = (primary_award or {}).get("suppliers") or []
    primary_supplier = suppliers[0] if suppliers else None
    award_value: dict[str, Any] = (primary_award or {}).get("value") or {}
    tender_value: dict[str, Any] = tender.get("value") or {}
    tender_period: dict[str, Any] = tender.get("tenderPeriod") or {}

    return NormalizedTender(
        ocid=ocid,
        tender_reference=tender.get("id") or ocid,
        title=tender.get("title") or compiled.get("name") or "(untitled)",
        description=tender.get("description"),
        procuring_entity_name=buyer.get("name"),
        procuring_entity_id=buyer.get("id"),
        procurement_method=tender.get("procurementMethod"),
        procurement_method_details=tender.get("procurementMethodDetails"),
        tender_status=tender.get("status"),
        tender_value_amount=_to_decimal(tender_value.get("amount")),
        tender_value_currency=tender_value.get("currency"),
        tender_period_start=_to_datetime(tender_period.get("startDate")),
        tender_period_end=_to_datetime(tender_period.get("endDate")),
        has_award=bool(awards),
        award_date=_to_datetime((primary_award or {}).get("date")),
        award_value_amount=_to_decimal(award_value.get("amount")),
        award_value_currency=award_value.get("currency"),
        contractor_name=(primary_supplier or {}).get("name"),
        contractor_id=(primary_supplier or {}).get("id"),
        financial_year=_extract_financial_year(compiled),
        location=_extract_location(tender),
        raw_ocds=record,
        source_url=source_url,
        raw_ocds_fingerprint=_fingerprint(record),
    )


def _to_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def _to_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    for fmt in _DATETIME_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def _extract_financial_year(compiled: dict[str, Any]) -> str | None:
    start = (
        (compiled.get("planning") or {})
        .get("budget", {})
        .get("period", {})
        .get("startDate")
    )
    if start and len(start) >= 4:
        year = int(start[:4])
        return f"{year}/{year + 1}"
    return None


def _extract_location(tender: dict[str, Any]) -> str | None:
    for item in tender.get("items") or []:
        desc = (item.get("deliveryLocation") or {}).get("description")
        if desc:
            return desc
    return None


def _fingerprint(record: dict[str, Any]) -> str:
    return hashlib.md5(
        json.dumps(record, sort_keys=True, default=str).encode()
    ).hexdigest()
