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
