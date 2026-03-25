"""Fuel price scrapers — EWURA cap prices (listing + in-memory PDF parse)."""

from __future__ import annotations

import logging

from src.core.base_scraper import BaseScraper
from src.core.config import load_settings
from src.core.http_client import ScraperHttpClient
from src.domains.energy.ewura.fetch import fetch_page
from src.domains.energy.ewura.listing import list_cap_price_documents_from_html
from src.domains.energy.ewura.models import EwuraParseOutcome, FilteredDocumentRef
from src.domains.energy.ewura.pdf_pipeline import fetch_and_parse_cap_price_pdf

logger = logging.getLogger(__name__)


class EwuraFuelScraper(BaseScraper):
    """Discover cap-price PDF/DOCX URLs and parse PDFs in memory (Phase 2)."""

    name = "ewura_fuel"

    def __init__(
        self,
        http_client: ScraperHttpClient | None = None,
        *,
        listing_url: str | None = None,
    ) -> None:
        self._settings = load_settings()
        self._listing_url = listing_url or self._settings.ewura_listing_url
        self._http = http_client or ScraperHttpClient(self._settings)
        self._should_close_client = http_client is None

    def _max_document_bytes(self) -> int:
        return int(self._settings.ewura_max_document_mb * 1024 * 1024)

    def list_cap_price_documents(self) -> list[FilteredDocumentRef]:
        """Fetch the listing page and return filtered document references."""
        html = fetch_page(self._http, self._listing_url)
        return list_cap_price_documents_from_html(html, self._listing_url)

    def fetch_and_parse_pdf(self, ref: FilteredDocumentRef) -> EwuraParseOutcome:
        """Download one PDF in memory; return rows or a structured error outcome."""
        return fetch_and_parse_cap_price_pdf(
            self._http,
            ref,
            max_bytes=self._max_document_bytes(),
        )

    def ingest_cap_price_pdfs(
        self,
        *,
        limit: int | None = None,
    ) -> list[EwuraParseOutcome]:
        """Parse all listed PDFs (DOCX skipped with ``unsupported_non_pdf``)."""
        refs = self.list_cap_price_documents()
        pdf_refs = [
            r
            for r in refs
            if str(r.url).lower().split("?", maxsplit=1)[0].endswith(".pdf")
        ]
        eff_limit = limit if limit is not None else self._settings.ewura_run_pdf_limit
        if eff_limit is not None:
            pdf_refs = pdf_refs[:eff_limit]
        return [self.fetch_and_parse_pdf(r) for r in pdf_refs]

    def run(self) -> None:
        outcomes = self.ingest_cap_price_pdfs()
        ok_n = sum(1 for o in outcomes if o.ok)
        logger.info(
            "ewura_fuel_ingest_complete",
            extra={
                "scraper": self.name,
                "documents_attempted": len(outcomes),
                "documents_ok": ok_n,
                "listing_url": self._listing_url,
            },
        )

    def close(self) -> None:
        if self._should_close_client:
            self._http.close()
