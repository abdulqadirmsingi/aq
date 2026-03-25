"""Resolve effective pricing dates from link text and PDF body snippets."""

from __future__ import annotations

import re
from datetime import date, datetime

from dateutil import parser as date_parser

# e.g. "4th March 2026", "1st November 2017"
_ORDINAL_DAY_FIRST = re.compile(
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,})\s+(\d{4})\b",
    re.IGNORECASE,
)

# ISO-like embedded in filenames or text
_ISO_DATE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")


def extract_effective_date(*text_blobs: str) -> date | None:
    """
    Best-effort effective date from listing title and/or document text.

    Tries explicit ordinal patterns first, then ``dateutil`` fuzzy parse.
    """
    combined = " ".join(t for t in text_blobs if t).strip()
    if not combined:
        return None

    for pattern in (_ORDINAL_DAY_FIRST,):
        match = pattern.search(combined)
        if match:
            day, mon, year = match.groups()
            try:
                guessed = date_parser.parse(
                    f"{day} {mon} {year}",
                    dayfirst=True,
                    yearfirst=False,
                )
            except (ValueError, OverflowError, TypeError):
                continue
            else:
                return guessed.date()

    iso_m = _ISO_DATE.search(combined)
    if iso_m:
        y, m, d = (int(iso_m.group(1)), int(iso_m.group(2)), int(iso_m.group(3)))
        try:
            return date(y, m, d)
        except ValueError:
            pass

    try:
        guessed = date_parser.parse(
            combined,
            fuzzy=True,
            dayfirst=True,
            default=datetime(2000, 1, 1),
        )
    except (ValueError, OverflowError, TypeError):
        return None
    if guessed.year < 1990 or guessed.year > 2100:
        return None
    return guessed.date()
