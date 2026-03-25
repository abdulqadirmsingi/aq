"""Turn detected cap-price tables into row-based fuel records."""

from __future__ import annotations

from dataclasses import replace
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
    Reuses the previous table's column map when a fragment has no header row
    (common when a cap-price table spans PDF pages).
    """
    records: list[FuelPriceRecord] = []
    warnings: list[str] = []
    last_cmap: ColumnMap | None = None
    for idx, table in enumerate(tables):
        cmap = HeaderDetector.detect(table)
        used_continuation = False
        if cmap is None and last_cmap is not None and _continuation_candidate(
            table,
            last_cmap,
        ):
            cmap = replace(last_cmap, header_row_index=-1)
            used_continuation = True
            warnings.append(f"table_{idx}_continuation")
        if cmap is None:
            warnings.append(f"table_{idx}_no_header")
            continue
        if not used_continuation:
            last_cmap = cmap
        chunk, w = _rows_from_table(table, cmap, effective_date)
        records.extend(chunk)
        warnings.extend(f"table_{idx}_{m}" for m in w)
    return records, warnings


def _table_width(table: list[list[str | None]]) -> int:
    return max((len(r) for r in table), default=0)


def _max_col_index(cmap: ColumnMap) -> int:
    cols = [cmap.location_col, cmap.petrol_col, cmap.diesel_col, cmap.kerosene_col]
    nums = [c for c in cols if c is not None]
    return max(nums) if nums else 0


def _continuation_candidate(
    table: list[list[str | None]],
    last_cmap: ColumnMap,
) -> bool:
    if not table or HeaderDetector.detect(table) is not None:
        return False
    need = _max_col_index(last_cmap) + 1
    if _table_width(table) < need:
        return False
    fuel_cols = [
        c
        for c in (
            last_cmap.petrol_col,
            last_cmap.diesel_col,
            last_cmap.kerosene_col,
        )
        if c is not None
    ]
    for row in table[:10]:
        if any(parse_price_cell(_cell_at(row, c)) is not None for c in fuel_cols):
            return True
    return False


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
