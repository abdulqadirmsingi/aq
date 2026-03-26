"""Phase 3: DOCX parsing, continuation tables, deduplication."""

from __future__ import annotations

from datetime import date
from io import BytesIO

from docx import Document

from src.domains.energy.ewura.docx_pipeline import parse_cap_price_docx_bytes
from src.domains.energy.ewura.extract_data import tables_to_fuel_records
from src.domains.energy.ewura.models import FuelPriceRecord
from src.domains.energy.ewura.records_dedupe import dedupe_fuel_records


def _sample_cap_price_docx_bytes() -> bytes:
    buf = BytesIO()
    doc = Document()
    doc.add_paragraph("Cap Prices for Petroleum Products effective 10th June 2025")
    table = doc.add_table(rows=3, cols=4)
    hdr = ("Town", "Petrol", "Diesel", "Kerosene")
    for i, h in enumerate(hdr):
        table.rows[0].cells[i].text = h
    table.rows[1].cells[0].text = "Morogoro"
    table.rows[1].cells[1].text = "3100"
    table.rows[1].cells[2].text = "3090"
    table.rows[1].cells[3].text = "3080"
    table.rows[2].cells[0].text = "Dodoma"
    table.rows[2].cells[1].text = "3110"
    table.rows[2].cells[2].text = "3105"
    table.rows[2].cells[3].text = "-"
    doc.save(buf)
    return buf.getvalue()


def test_parse_cap_price_docx_bytes_synthetic() -> None:
    raw = _sample_cap_price_docx_bytes()
    out = parse_cap_price_docx_bytes(
        raw,
        document_url="https://www.ewura.go.tz/uploads/documents/test.docx",
        link_text="Cap Prices June 2025",
        content_sha256="b" * 64,
    )
    assert out.ok
    assert out.payload is not None
    assert out.payload.published_date == "2025-06-10"
    assert len(out.payload.data) >= 5
    locs = {r.location for r in out.payload.data}
    assert "Morogoro" in locs and "Dodoma" in locs


def test_continuation_table_reuses_column_map() -> None:
    tables = [
        [["Town", "Petrol", "Diesel"], ["Alpha", "100", "200"]],
        [["", "300", "400"], ["Beta", "500", "600"]],
    ]
    recs, warnings = tables_to_fuel_records(
        tables,
        effective_date=date(2025, 1, 1),
    )
    assert any("continuation" in w for w in warnings)
    locs = {r.location for r in recs}
    assert "Alpha" in locs and "Beta" in locs


def test_dedupe_fuel_records() -> None:
    d = date(2025, 1, 1)
    rows = [
        FuelPriceRecord(
            location="Dar es Salaam",
            fuel_type="petrol",
            price=2000,
            recorded_at=d,
        ),
        FuelPriceRecord(
            location="Dar es Salaam",
            fuel_type="petrol",
            price=2000,
            recorded_at=d,
        ),
        FuelPriceRecord(
            location="Dar es Salaam",
            fuel_type="diesel",
            price=1900,
            recorded_at=d,
        ),
    ]
    out = dedupe_fuel_records(rows)
    assert len(out) == 2


def test_tables_to_fuel_records_skips_numeric_location_cells() -> None:
    tables = [
        [
            ["S/N", "Town", "Petrol", "Diesel"],
            ["1", "Dodoma", "100", "200"],
            ["2", "Morogoro", "110", "210"],
        ],
    ]
    recs, _warnings = tables_to_fuel_records(
        tables,
        effective_date=date(2025, 1, 1),
    )
    assert {r.location for r in recs} == {"Dodoma", "Morogoro"}


def test_tables_to_fuel_records_classifies_decimal_port_table_as_wholesale() -> None:
    tables = [
        [
            ["Port", "Petrol", None, None, "Diesel", None, None, "Kerosene"],
            ["Dar es Salaam", None, "100.25", None, None, "200.50", None, None, "300.75"],
        ],
        [
            ["S.No", "Town", "Cap Prices", None, None],
            [None, None, "Petrol", "Diesel", "Kerosene"],
            ["1", "Dodoma", "100", "200", "300"],
        ],
    ]

    recs, warnings = tables_to_fuel_records(
        tables,
        effective_date=date(2025, 1, 1),
    )

    assert {r.location for r in recs} == {"Dar es Salaam", "Dodoma"}
    assert {r.market_segment for r in recs if r.location == "Dar es Salaam"} == {"wholesale"}
    assert {r.market_segment for r in recs if r.location == "Dodoma"} == {"retail"}


def test_tables_to_fuel_records_skips_lower_quality_duplicate_retail_table() -> None:
    tables = [
        [
            ["S.No", "Town", "Cap Prices", None, None],
            [None, None, "Petrol", "Diesel", "Kerosene"],
            ["1", "Uvinza (Lugufu)", "100", "200", "300"],
            ["2", "Mkwajuni", "110", "210", "310"],
        ],
        [
            [None, None, None, None, None, None],
            ["S.No", None, "Town", None, None, None],
            [None, None, None, "Petrol", "Diesel", "Kerosene"],
            ["1", "Uvinza (Lugufu", ")", "100", "200", "300"],
            ["2", "Mkwa", "juni", "110", "210", "310"],
        ],
    ]

    recs, warnings = tables_to_fuel_records(
        tables,
        effective_date=date(2025, 1, 1),
    )

    assert len(recs) == 6
    assert {r.location for r in recs} == {"Uvinza (Lugufu)", "Mkwajuni"}
    assert any("duplicate_table" in warning for warning in warnings)
