from __future__ import annotations

from datetime import UTC, date, datetime, time
from decimal import Decimal, InvalidOperation

from dateutil import parser

from src.domains.money.fx_models import ExchangeRateDetailPayload


def parse_decimal_number(raw_value: str) -> Decimal:
    cleaned = raw_value.strip().replace(",", "")
    if not cleaned:
        raise ValueError("Numeric value is empty.")
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid numeric value: {raw_value!r}") from exc


def build_recorded_at(value: date, *, hour: int = 0, minute: int = 0) -> datetime:
    return datetime.combine(value, time(hour=hour, minute=minute, tzinfo=UTC))


def parse_source_timestamp(raw_value: str, *, default_tz: UTC = UTC) -> datetime:
    parsed = parser.parse(raw_value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=default_tz)
    return parsed.astimezone(UTC)


def build_external_reference(
    *,
    instrument_code: str,
    metric_slug: str,
    channel: str | None,
    cash_note_band: str | None,
    source_effective_date: date | None,
) -> str:
    effective_date = (
        source_effective_date.isoformat() if source_effective_date else "na"
    )
    return "|".join(
        [
            instrument_code.upper(),
            metric_slug,
            channel or "na",
            cash_note_band or "na",
            effective_date,
        ]
    )


def compute_inverse_rate(value: Decimal) -> Decimal | None:
    if value == 0:
        return None
    return Decimal("1") / value


def payload_fingerprint(
    *,
    value: Decimal,
    unit_override: str,
    detail: ExchangeRateDetailPayload,
    extra_data: dict[str, object],
    ingestion_metadata: dict[str, object],
) -> tuple[object, ...]:
    return (
        value,
        unit_override,
        detail.instrument_code,
        detail.instrument_name,
        detail.instrument_type,
        detail.quote_code,
        detail.rate_kind,
        detail.market_scope,
        detail.channel,
        detail.cash_note_band,
        detail.source_effective_date,
        detail.source_last_updated_at,
        detail.inverse_rate,
        tuple(sorted(extra_data.items())),
        tuple(sorted(ingestion_metadata.items())),
    )
