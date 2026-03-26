"""De-duplicate fuel rows produced from multi-table or repeated PDF regions."""

from __future__ import annotations

from datetime import date

from src.domains.energy.ewura.models import FuelPriceRecord


def dedupe_fuel_records(records: list[FuelPriceRecord]) -> list[FuelPriceRecord]:
    """Keep first occurrence per (location, market_segment, fuel_type, recorded_at)."""
    seen: set[tuple[str, str, str, date]] = set()
    out: list[FuelPriceRecord] = []
    for rec in records:
        key = (
            rec.location.lower().strip(),
            rec.market_segment,
            rec.fuel_type,
            rec.recorded_at,
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out
