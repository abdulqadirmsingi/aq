"""Phase 1: EWURA listing — link extraction and filtering (no network)."""

from __future__ import annotations

import httpx

from src.core.http_client import ScraperHttpClient
from src.domains.energy.ewura.filters import filter_documents
from src.domains.energy.ewura.links import extract_document_links
from src.domains.energy.ewura.listing import list_cap_price_documents_from_html
from src.domains.energy.ewura.models import DocumentLink
from src.domains.energy.fuel_scraper import EwuraFuelScraper

_PAGE = "https://www.ewura.go.tz/pages/petroleum-product-pricing"

_SAMPLE_HTML = """
<!DOCTYPE html>
<html>
  <body>
    <a href="/uploads/documents/en-cap-prices-march-2026.pdf">
      Cap Prices for Petroleum Products March 2026
    </a>
    <a href="/uploads/documents/en-july-2025.docx">
      Cap Prices for July 2025 English
    </a>
    <a href="https://www.ewura.go.tz/wp-content/uploads/Petroleum-Products-Price-Setting-Rules.pdf">
      Rules
    </a>
    <a href="/uploads/documents/en-unrelated.pdf">Minutes of meeting 2024</a>
    <a href="/uploads/documents/en-cap-prices-march-2026.pdf">duplicate same url</a>
    <a href="#section">anchor only</a>
  </body>
</html>
"""


def test_extract_document_links_dedupes_and_extensions() -> None:
    links = extract_document_links(_SAMPLE_HTML, _PAGE)
    urls = [str(link.url) for link in links]
    assert len(links) == 4
    assert len(set(urls)) == len(urls)
    assert any(u.endswith(".pdf") for u in urls)
    assert any(u.endswith(".docx") for u in urls)
    assert "wp-content" in " ".join(urls)


def test_filter_documents_keeps_cap_price_uploads_only() -> None:
    links = extract_document_links(_SAMPLE_HTML, _PAGE)
    filtered = filter_documents(links)
    texts = {f.link_text.strip() for f in filtered}
    assert len(filtered) == 2
    assert any("March 2026" in t for t in texts)
    assert any("July 2025" in t for t in texts)


def test_list_cap_price_documents_from_html_matches_filter_pipeline() -> None:
    combined = list_cap_price_documents_from_html(_SAMPLE_HTML, _PAGE)
    assert len(combined) == 2


def test_filter_accepts_bei_kikomo_swahili_filename() -> None:
    html = """
    <html><body>
    <a href="/uploads/documents/en-bei-kikomo-jan-2025.pdf">January prices</a>
    </body></html>
    """
    links = extract_document_links(html, _PAGE)
    filtered = filter_documents(links)
    assert len(filtered) == 1


def test_ewura_fuel_scraper_mocked_http() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "www.ewura.go.tz"
        return httpx.Response(200, text=_SAMPLE_HTML)

    transport = httpx.MockTransport(handler)
    client = ScraperHttpClient(transport=transport)
    try:
        scraper = EwuraFuelScraper(
            http_client=client,
            listing_url="https://www.ewura.go.tz/pages/petroleum-product-pricing",
        )
        docs = scraper.list_cap_price_documents()
        assert len(docs) == 2
    finally:
        client.close()


def test_document_link_from_relative_path() -> None:
    link = DocumentLink(
        url="https://www.ewura.go.tz/uploads/documents/x.pdf",
        link_text="Cap Prices for Petroleum Products",
    )
    assert "petroleum" in link.link_text.lower()
