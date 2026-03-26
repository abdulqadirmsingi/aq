"""Helpers for inferring and normalizing Tanzania energy location groupings."""

from __future__ import annotations

import re

TZ_COUNTRY_NAME = "Tanzania"

TZ_REGION_NAMES = (
    "Arusha",
    "Dar es Salaam",
    "Dodoma",
    "Geita",
    "Iringa",
    "Kagera",
    "Katavi",
    "Kigoma",
    "Kilimanjaro",
    "Lindi",
    "Manyara",
    "Mara",
    "Mbeya",
    "Mjini Magharibi",
    "Morogoro",
    "Mtwara",
    "Mwanza",
    "Njombe",
    "Pemba North",
    "Pemba South",
    "Pwani",
    "Rukwa",
    "Ruvuma",
    "Shinyanga",
    "Simiyu",
    "Singida",
    "Songwe",
    "Tabora",
    "Tanga",
    "Unguja North",
    "Unguja South",
)

_TZ_REGION_SET = {name.casefold(): name for name in TZ_REGION_NAMES}


def is_country_name(value: str | None) -> bool:
    return (value or "").strip().casefold() == TZ_COUNTRY_NAME.casefold()


def infer_tanzania_region_name(*values: str | None) -> str | None:
    for value in values:
        normalized = _match_region_name(value)
        if normalized is not None:
            return normalized
    return None


def _match_region_name(value: str | None) -> str | None:
    if not value:
        return None

    cleaned = value.strip()
    direct = _TZ_REGION_SET.get(cleaned.casefold())
    if direct is not None:
        return direct

    prefix_match = re.match(r"^(.*?)\s*\(", cleaned)
    if prefix_match is None:
        return None

    prefix = prefix_match.group(1).strip()
    return _TZ_REGION_SET.get(prefix.casefold())
