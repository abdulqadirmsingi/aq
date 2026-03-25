"""Normalize numeric cells from EWURA tables."""

from __future__ import annotations

import re


def parse_price_cell(raw: str | None) -> int | None:
    """
    Parse a cap price integer from messy table text.

    Strips currency words, thousands separators, and whitespace.
    Returns ``None`` for blanks, dashes, or non-numeric values.
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s in {"-", "—", "–", "n/a", "na", "*"}:
        return None
    if "%" in s:
        return None
    s = re.sub(r"(?i)\s*(tzs|tsh|tshs|/l|per\s*litre?)\s*", "", s)
    s = s.replace(",", "").replace(" ", "").strip()
    match = re.search(r"-?\d+(?:\.\d+)?", s)
    if not match:
        return None
    try:
        value = float(match.group())
    except ValueError:
        return None
    if value < 0:
        return None
    return int(round(value))
