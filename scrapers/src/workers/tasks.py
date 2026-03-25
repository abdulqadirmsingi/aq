"""Celery task definitions — domain scrapers."""

from __future__ import annotations

from src.core.config import load_settings
from src.core.fingerprint_store import DocumentFingerprintStore
from src.domains.energy.fuel_scraper import EwuraFuelScraper
from src.workers.celery_app import app


@app.task(name="scrapers.run_ewura_fuel")
def run_ewura_fuel_scraper() -> dict[str, int]:
    """List and ingest EWURA cap-price PDF/DOCX; optional fingerprint dedupe."""
    settings = load_settings()
    store: DocumentFingerprintStore | None = None
    if settings.database_url:
        store = DocumentFingerprintStore(settings.database_url, "ewura_fuel")
    scraper = EwuraFuelScraper()
    try:
        outcomes = scraper.ingest_cap_price_documents(fingerprint_store=store)
    finally:
        scraper.close()
        if store is not None:
            store.close()
    return {
        "attempted": len(outcomes),
        "ok": sum(1 for o in outcomes if o.ok),
        "skipped": sum(1 for o in outcomes if o.skipped),
    }
