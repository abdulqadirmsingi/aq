"""Dynamic header row and fuel column detection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ColumnMap:
    """Maps logical fields to zero-based column indices."""

    header_row_index: int
    location_col: int
    petrol_col: int | None
    diesel_col: int | None
    kerosene_col: int | None


class HeaderDetector:
    """Match petrol / diesel / kerosene columns by header synonyms (EN/SW)."""

    _FUEL_SYNONYMS: ClassVar[dict[str, tuple[str, ...]]] = {
        "petrol": (
            "petrol",
            "gasoline",
            "unleaded",
            "pms",
            "premium motor",
            "petroli",
        ),
        "diesel": (
            "diesel",
            "ago",
            "gas oil",
            "automotive gas oil",
            "dizeli",
        ),
        "kerosene": (
            "kerosene",
            "paraffin",
            "illuminating",
            "iko",
            "kerosine",
        ),
    }
    _LOCATION_KEYWORDS: ClassVar[tuple[str, ...]] = (
        "town",
        "city",
        "location",
        "place",
        "region",
        "district",
        "ward",
        "mkoa",
        "jiji",
        "eneo",
        "area",
        "depot",
    )
    _SERIAL_KEYWORDS: ClassVar[tuple[str, ...]] = (
        "s n",
        "sn",
        "no",
        "number",
        "serial",
        "id",
    )

    @classmethod
    def detect(cls, table: list[list[str | None]]) -> ColumnMap | None:
        if not table:
            return None
        max_scan = min(len(table), 20)
        for row_idx in range(max_scan):
            row = table[row_idx]
            if not row:
                continue
            norms = [_normalize_cell(c) for c in row]
            candidates: list[tuple[int, str, int]] = []
            for col_idx, norm in enumerate(norms):
                for fuel, syns in cls._FUEL_SYNONYMS.items():
                    for syn in syns:
                        if syn in norm:
                            candidates.append((col_idx, fuel, len(syn)))
            candidates.sort(key=lambda x: -x[2])
            assigned_cols: set[int] = set()
            assigned_fuels: set[str] = set()
            fuel_to_col: dict[str, int] = {}
            for col_idx, fuel, _score in candidates:
                if col_idx in assigned_cols or fuel in assigned_fuels:
                    continue
                assigned_cols.add(col_idx)
                assigned_fuels.add(fuel)
                fuel_to_col[fuel] = col_idx
            if len(assigned_fuels) < 2:
                continue
            location_col = cls._pick_location_col(norms, assigned_cols)
            return ColumnMap(
                header_row_index=row_idx,
                location_col=location_col,
                petrol_col=fuel_to_col.get("petrol"),
                diesel_col=fuel_to_col.get("diesel"),
                kerosene_col=fuel_to_col.get("kerosene"),
            )
        return None

    @staticmethod
    def _pick_location_col(row_norms: list[str], fuel_cols: set[int]) -> int:
        candidates = [j for j in range(len(row_norms)) if j not in fuel_cols]
        if not candidates:
            return 0

        for col in candidates:
            norm = row_norms[col]
            if any(keyword in norm for keyword in HeaderDetector._LOCATION_KEYWORDS):
                return col

        non_serial = [
            col
            for col in candidates
            if not any(keyword == row_norms[col] for keyword in HeaderDetector._SERIAL_KEYWORDS)
        ]
        if non_serial:
            return non_serial[0]
        return candidates[0]


def _normalize_cell(cell: str | None) -> str:
    if cell is None:
        return ""
    s = str(cell).lower().strip()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()
