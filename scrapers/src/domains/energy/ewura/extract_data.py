"""Turn detected cap-price tables into row-based fuel records."""

from __future__ import annotations

import re
from dataclasses import replace
from datetime import date

from src.domains.energy.ewura.headers import ColumnMap, HeaderDetector
from src.domains.energy.ewura.models import FuelMarketSegment, FuelPriceRecord, FuelType
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
    last_cmap_by_market: dict[FuelMarketSegment, ColumnMap] = {}
    accepted_chunks_by_market: dict[FuelMarketSegment, list[list[FuelPriceRecord]]] = {
        "retail": [],
        "wholesale": [],
    }
    for idx, table in enumerate(tables):
        cmap = HeaderDetector.detect(table)
        used_continuation = False
        market_segment: FuelMarketSegment | None = None
        continuation_market: FuelMarketSegment | None = None
        if cmap is None:
            continuation_market = _continuation_market_segment(table, last_cmap_by_market)
        if (
            cmap is None
            and continuation_market is not None
        ):
            cmap = replace(last_cmap_by_market[continuation_market], header_row_index=-1)
            used_continuation = True
            market_segment = continuation_market
            warnings.append(f"table_{idx}_continuation")
        if cmap is None:
            warnings.append(f"table_{idx}_no_header")
            continue
        market_segment = market_segment or _table_market_segment(table, cmap)
        if market_segment is None:
            warnings.append(f"table_{idx}_non_retail")
            continue
        if not used_continuation:
            last_cmap = cmap
            last_cmap_by_market[market_segment] = cmap
        chunk, w = _rows_from_table(table, cmap, effective_date, market_segment)
        if chunk and _is_lower_quality_duplicate_chunk(chunk, accepted_chunks_by_market[market_segment]):
            warnings.append(f"table_{idx}_duplicate_table")
            warnings.extend(f"table_{idx}_{m}" for m in w)
            continue
        if chunk:
            accepted_chunks_by_market[market_segment].append(chunk)
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
        parsed_prices = [
            parse_price_cell(_cell_at(row, c))
            for c in fuel_cols
            if parse_price_cell(_cell_at(row, c)) is not None
        ]
        if len(parsed_prices) >= 2:
            return True
    return False


def _continuation_market_segment(
    table: list[list[str | None]],
    last_cmap_by_market: dict[FuelMarketSegment, ColumnMap],
) -> FuelMarketSegment | None:
    for market_segment, last_cmap in last_cmap_by_market.items():
        if _continuation_candidate(table, last_cmap):
            return market_segment
    return None


def _rows_from_table(
    table: list[list[str | None]],
    cmap: ColumnMap,
    effective_date: date,
    market_segment: FuelMarketSegment,
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
        loc = _normalize_location(loc_cell)
        if loc:
            last_location = loc
        elif last_location:
            loc = last_location
        else:
            continue
        if _looks_like_header_again(loc) or _looks_like_bad_location(loc):
            continue
        parsed_prices: list[tuple[FuelType, int]] = []
        for fuel_type, col in fuel_specs:
            price = _price_from_row(row, col)
            if price is None:
                continue
            parsed_prices.append((fuel_type, price))
        if len(parsed_prices) < 2:
            continue
        for fuel_type, price in parsed_prices:
            out.append(
                FuelPriceRecord(
                    location=loc,
                    market_segment=market_segment,
                    fuel_type=fuel_type,
                    price=price,
                    recorded_at=effective_date,
                ),
            )
    if not out:
        warn.append("no_data_rows")
    return out, warn


def _table_market_segment(
    table: list[list[str | None]],
    cmap: ColumnMap,
) -> FuelMarketSegment | None:
    header_rows = table[: max(cmap.header_row_index + 2, 2)]
    header_text = " ".join(
        _normalize_text(cell)
        for row in header_rows
        for cell in row
        if cell
    )
    location_header = " ".join(
        _normalize_text(_cell_at(row, cmap.location_col))
        for row in header_rows
    ).strip()

    retail_markers = (
        "retail",
        "cap prices",
        "town",
        "city",
        "district",
        "region",
        "location",
        "s no",
    )
    wholesale_markers = (
        "wholesale",
        "fob",
        "premium",
        "premiums",
        "port charges",
        "exchange rates",
        "port",
    )

    has_retail_signal = any(marker in header_text for marker in retail_markers) or any(
        marker in location_header for marker in ("town", "city", "district", "region", "location")
    )
    has_wholesale_signal = any(marker in header_text for marker in wholesale_markers) or (
        "port" in location_header and "town" not in location_header
    )

    if has_wholesale_signal:
        return "wholesale"
    if has_retail_signal:
        return "retail"
    return None


def _is_lower_quality_duplicate_chunk(
    chunk: list[FuelPriceRecord],
    accepted_chunks: list[list[FuelPriceRecord]],
) -> bool:
    chunk_bundles = _location_price_bundles(chunk)
    if not chunk_bundles:
        return False

    chunk_quality = _chunk_quality(chunk)
    chunk_bundle_set = set(chunk_bundles)
    for accepted in accepted_chunks:
        accepted_bundles = _location_price_bundles(accepted)
        if not accepted_bundles:
            continue
        accepted_bundle_set = set(accepted_bundles)
        overlap = len(chunk_bundle_set & accepted_bundle_set)
        smaller = min(len(chunk_bundle_set), len(accepted_bundle_set))
        if smaller == 0:
            continue
        if overlap / smaller >= 0.8 and chunk_quality <= _chunk_quality(accepted):
            return True
    return False


def _location_price_bundles(chunk: list[FuelPriceRecord]) -> list[tuple[tuple[str, int], ...]]:
    bundles: list[tuple[tuple[str, int], ...]] = []
    current_location: str | None = None
    current_bundle: list[tuple[str, int]] = []
    for record in chunk:
        if current_location != record.location:
            if current_bundle:
                bundles.append(tuple(sorted(current_bundle)))
            current_location = record.location
            current_bundle = []
        current_bundle.append((record.fuel_type, record.price))
    if current_bundle:
        bundles.append(tuple(sorted(current_bundle)))
    return bundles


def _chunk_quality(chunk: list[FuelPriceRecord]) -> int:
    locations = [bundle_location for bundle_location in _ordered_chunk_locations(chunk)]
    alpha_chars = sum(sum(1 for ch in location if ch.isalpha()) for location in locations)
    complete_names = sum(
        1
        for location in locations
        if len(location) >= 4
        and location[0].isalnum()
        and location[-1].isalnum()
    )
    return len(locations) * 20 + alpha_chars + complete_names * 10


def _ordered_chunk_locations(chunk: list[FuelPriceRecord]) -> list[str]:
    out: list[str] = []
    current_location: str | None = None
    for record in chunk:
        if record.location != current_location:
            out.append(record.location)
            current_location = record.location
    return out


def _cell_at(row: list[str | None], col: int) -> str | None:
    if col < 0 or col >= len(row):
        return None
    return row[col]


def _price_from_row(row: list[str | None], col: int) -> int | None:
    for candidate_col in range(max(0, col - 1), min(len(row), col + 3)):
        price = parse_price_cell(_cell_at(row, candidate_col))
        if price is not None:
            return price
    return None


def _row_blank(row: list[str | None]) -> bool:
    return all(c is None or str(c).strip() == "" for c in row)


def _looks_like_header_again(location: str) -> bool:
    """Skip rows that look like a repeated header line."""
    loc_norm = location.lower().strip()
    header_tokens = {
        "petrol",
        "diesel",
        "kerosene",
        "cap price",
        "cap prices",
        "prices",
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
    return loc_norm in header_tokens or ("cap" in loc_norm and "price" in loc_norm)


def _normalize_location(cell: str | None) -> str:
    if cell is None:
        return ""
    return " ".join(str(cell).strip().split())


def _looks_like_bad_location(location: str) -> bool:
    loc_norm = location.lower().strip()
    if len(loc_norm) < 2:
        return True
    if parse_price_cell(location) is not None:
        return True
    return not any(ch.isalpha() for ch in loc_norm)


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()
