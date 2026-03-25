"""Fuel price scrapers — EWURA cap prices (Phase 1: listing only)."""

from __future__ import annotations

import logging

from src.core.base_scraper import BaseScraper
from src.core.config import load_settings
from src.core.http_client import ScraperHttpClient
from src.domains.energy.ewura.fetch import fetch_page
from src.domains.energy.ewura.listing import list_cap_price_documents_from_html
from src.domains.energy.ewura.models import FilteredDocumentRef

logger = logging.getLogger(__name__)


class EwuraFuelScraper(BaseScraper):
    """Discover cap-price PDF/DOCX URLs from the EWURA petroleum pricing page."""

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

    def list_cap_price_documents(self) -> list[FilteredDocumentRef]:
        """Fetch the listing page and return filtered document references."""
        html = fetch_page(self._http, self._listing_url)
        return list_cap_price_documents_from_html(html, self._listing_url)

    def run(self) -> None:
        """Phase 1: log how many cap-price documents were discovered."""
        documents = self.list_cap_price_documents()
        logger.info(
            "ewura_fuel_listing_complete",
            extra={
                "scraper": self.name,
                "documents_found": len(documents),
                "listing_url": self._listing_url,
            },
        )

    def close(self) -> None:
        if self._should_close_client:
            self._http.close()
