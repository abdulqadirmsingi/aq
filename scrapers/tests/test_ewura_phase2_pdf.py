"""Phase 2–3: PDF/DOCX parsing helpers and synthetic PDF fixtures."""

from __future__ import annotations

from io import BytesIO

import httpx
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.core.http_client import ScraperHttpClient
from src.domains.energy.ewura.document_pipeline import (
    fetch_and_parse_cap_price_document,
)
from src.domains.energy.ewura.headers import HeaderDetector
from src.domains.energy.ewura.models import FilteredDocumentRef
from src.domains.energy.ewura.numbers import parse_price_cell
from src.domains.energy.ewura.pdf_pipeline import parse_cap_price_pdf_bytes
from src.domains.energy.fuel_scraper import EwuraFuelScraper


def test_parse_price_cell() -> None:
    assert parse_price_cell("2,118") == 2118
    assert parse_price_cell(" 2110 TZS ") == 2110
    assert parse_price_cell("2,125.4") == 2125
    assert parse_price_cell("-") is None
    assert parse_price_cell(None) is None
    assert parse_price_cell("n/a") is None
    assert parse_price_cell("-5.41%") is None


def test_header_detector_finds_fuels() -> None:
    table = [
        ["Town", "Petrol", "Diesel", "Kerosene"],
        ["Dar", "100", "200", "300"],
    ]
    cmap = HeaderDetector.detect(table)
    assert cmap is not None
    assert cmap.petrol_col == 1
    assert cmap.diesel_col == 2
    assert cmap.kerosene_col == 3
    assert cmap.location_col == 0


def test_header_detector_prefers_town_over_serial_column() -> None:
    table = [
        ["S/N", "Town", "Petrol", "Diesel", "Kerosene"],
        ["1", "Dar es Salaam", "100", "200", "300"],
    ]
    cmap = HeaderDetector.detect(table)
    assert cmap is not None
    assert cmap.location_col == 1


def test_header_detector_uses_previous_header_row_for_location_column() -> None:
    table = [
        ["S.No", "Town", "Cap Prices", None, None],
        [None, None, "Petrol", "Diesel", "Kerosene"],
        ["1", "Dodoma", "100", "200", "300"],
    ]
    cmap = HeaderDetector.detect(table)
    assert cmap is not None
    assert cmap.header_row_index == 1
    assert cmap.location_col == 1


def _sample_cap_price_pdf_bytes() -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(
            "Cap Prices for Petroleum Products effective 4th March 2026",
            styles["Title"],
        ),
        Spacer(1, 12),
    ]
    data = [
        ["Town", "Petrol (TZS/L)", "Diesel (TZS/L)", "Kerosene (TZS/L)"],
        ["Dar es Salaam", "2,118", "2110", "2100"],
        ["Arusha", "2130", "2,125.4", "-"],
    ]
    tbl = Table(data)
    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ],
        ),
    )
    story.append(tbl)
    doc.build(story)
    return buf.getvalue()


def test_parse_cap_price_pdf_bytes_synthetic() -> None:
    raw = _sample_cap_price_pdf_bytes()
    out = parse_cap_price_pdf_bytes(
        raw,
        document_url="https://www.ewura.go.tz/uploads/documents/test.pdf",
        link_text="Cap Prices effective 4th March 2026",
        content_sha256="a" * 64,
    )
    assert out.ok
    assert out.payload is not None
    assert out.payload.published_date == "2026-03-04"
    assert len(out.payload.data) >= 5
    kinds = {r.fuel_type for r in out.payload.data}
    assert "petrol" in kinds and "diesel" in kinds
    assert all(r.price < 100_000 for r in out.payload.data)


def test_fetch_and_parse_rejects_unknown_extension() -> None:
    ref = FilteredDocumentRef(
        url=(
            "https://www.ewura.go.tz/uploads/documents/"
            "en-cap-prices-petroleum-weird.xyz"
        ),
        link_text="Cap Prices Petroleum 2026",
    )
    transport = httpx.MockTransport(lambda _r: httpx.Response(200))
    client = ScraperHttpClient(transport=transport)
    try:
        out = fetch_and_parse_cap_price_document(client, ref, max_bytes=10_000_000)
    finally:
        client.close()
    assert out.ok is False
    assert out.error == "unsupported_format"


def test_ewura_fuel_scraper_end_to_end_mock_pdf() -> None:
    pdf = _sample_cap_price_pdf_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if u.endswith("petroleum-product-pricing"):
            return httpx.Response(
                200,
                text=(
                    '<html><body><a href="/uploads/documents/en-test.pdf">'
                    "Cap Prices for Petroleum Products March 2026</a></body></html>"
                ),
            )
        if "en-test.pdf" in u:
            return httpx.Response(200, content=pdf)
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = ScraperHttpClient(transport=transport)
    try:
        scraper = EwuraFuelScraper(
            http_client=client,
            listing_url="https://www.ewura.go.tz/pages/petroleum-product-pricing",
        )
        outcomes = scraper.ingest_cap_price_documents()
        assert len(outcomes) == 1
        assert outcomes[0].ok
        assert outcomes[0].payload and len(outcomes[0].payload.data) >= 1
    finally:
        client.close()
