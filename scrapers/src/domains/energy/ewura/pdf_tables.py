"""Read table grids from PDF bytes using pdfplumber."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import pdfplumber

# EWURA PDFs and test fixtures vary; prefer explicit ruling lines, then text flow.
_TABLE_SETTINGS: tuple[dict[str, Any], ...] = (
    {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
    {},
    {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "intersection_tolerance": 8,
        "text_tolerance": 3,
        "text_x_tolerance": 3,
        "text_y_tolerance": 3,
    },
)


def extract_tables_from_pdf(
    pdf_bytes: bytes,
) -> tuple[list[list[list[str | None]]], str]:
    """
    Return all tables from all pages plus first-page plain text (for dates).

    Tables are ``list[row][col]`` with ``None`` for empty cells.
    """
    all_tables: list[list[list[str | None]]] = []
    first_page_text = ""
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page_index, page in enumerate(pdf.pages):
            if page_index == 0:
                first_page_text = page.extract_text() or ""
            for raw in _extract_tables_from_page(page):
                normalized: list[list[str | None]] = []
                for row in raw:
                    normalized.append([_normalize_pdf_cell(c) for c in row])
                if normalized:
                    all_tables.append(normalized)
    return all_tables, first_page_text


def _extract_tables_from_page(page: pdfplumber.page.Page) -> list[list[list[Any]]]:
    tables: list[list[list[Any]]] = []
    seen: set[tuple[tuple[str, ...], ...]] = set()
    for settings in _TABLE_SETTINGS:
        for table in page.extract_tables(table_settings=settings) or []:
            fingerprint = _table_fingerprint(table)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            tables.append(table)
    return tables


def _table_fingerprint(table: list[list[Any]]) -> tuple[tuple[str, ...], ...]:
    return tuple(
        tuple("" if cell is None else str(cell).strip() for cell in row)
        for row in table
    )


def _normalize_pdf_cell(cell: object | None) -> str | None:
    if cell is None:
        return None
    s = str(cell).replace("\n", " ").strip()
    return s if s else None
