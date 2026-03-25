"""Turn detected cap-price tables into row-based fuel records."""

from __future__ import annotations

from datetime import date

from src.domains.energy.ewura.headers import ColumnMap, HeaderDetector
from src.domains.energy.ewura.models import FuelPriceRecord, FuelType
from src.domains.energy.ewura.numbers import parse_price_cell


def tables_to_fuel_records(
    tables: list[list[list[str | None]]],
    *,
    effective_date: date,
) -> tuple[list[FuelPriceRecord], list[str]]:
    """
    Parse all tables; accumulate records and human-readable warnings.

    Carries forward the last non-empty location when continuation rows omit it.
    """
    records: list[FuelPriceRecord] = []
    warnings: list[str] = []
    for idx, table in enumerate(tables):
        cmap = HeaderDetector.detect(table)
        if cmap is None:
            warnings.append(f"table_{idx}_no_header")
            continue
        chunk, w = _rows_from_table(table, cmap, effective_date)
        records.extend(chunk)
        warnings.extend(f"table_{idx}_{m}" for m in w)
    return records, warnings


def _rows_from_table(
    table: list[list[str | None]],
    cmap: ColumnMap,
    effective_date: date,
) -> tuple[list[FuelPriceRecord], list[str]]:
    out: list[FuelPriceRecord] = []
    warn: list[str] = []
    last_location = ""
    fuel_specs: list[tuple[FuelType, int]] = []
    if cmap.petrol_col is not None:
        fuel_specs.append(("petrol", cmap.petrol_col))
    if cmap.diesel_col is not None:
        fuel_specs.append(("diesel", cmap.diesel_col))
    if cmap.kerosene_col is not None:
        fuel_specs.append(("kerosene", cmap.kerosene_col))
    if not fuel_specs:
        return [], ["no_fuel_columns"]

    for row in table[cmap.header_row_index + 1 :]:
        if _row_blank(row):
            continue
        loc_cell = _cell_at(row, cmap.location_col)
        loc = str(loc_cell).strip() if loc_cell else ""
        if loc:
            last_location = loc
        elif last_location:
            loc = last_location
        else:
            continue
        if _looks_like_header_again(loc):
            continue
        for fuel_type, col in fuel_specs:
            price = parse_price_cell(_cell_at(row, col))
            if price is None:
                continue
            out.append(
                FuelPriceRecord(
                    location=loc,
                    fuel_type=fuel_type,
                    price=price,
                    recorded_at=effective_date,
                ),
            )
    if not out:
        warn.append("no_data_rows")
    return out, warn


def _cell_at(row: list[str | None], col: int) -> str | None:
    if col < 0 or col >= len(row):
        return None
    return row[col]


def _row_blank(row: list[str | None]) -> bool:
    return all(c is None or str(c).strip() == "" for c in row)


def _looks_like_header_again(location: str) -> bool:
    """Skip rows that look like a repeated header line."""
    loc_norm = location.lower().strip()
    header_tokens = {
        "petrol",
        "diesel",
        "kerosene",
        "pms",
        "ago",
        "paraffin",
        "town",
        "region",
        "location",
        "place",
        "jiji",
        "mkoa",
    }
    return loc_norm in header_tokens
