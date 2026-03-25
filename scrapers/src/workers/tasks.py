"""Celery task definitions — domain scrapers."""

from __future__ import annotations

from src.domains.energy.fuel_scraper import EwuraFuelScraper
from src.domains.money.bot_exchange_rate_scraper import BotExchangeRateScraper
from src.workers.celery_app import app


@app.task(name="scrapers.run_ewura_fuel")
def run_ewura_fuel_scraper() -> dict[str, int]:
    """List and ingest EWURA cap-price PDF/DOCX; optional fingerprint dedupe."""
    scraper = EwuraFuelScraper()
    try:
        outcomes = scraper.run()
    finally:
        scraper.close()
    return {
        "attempted": len(outcomes),
        "ok": sum(1 for o in outcomes if o.ok),
        "skipped": sum(1 for o in outcomes if o.skipped),
    }


@app.task(name="scrapers.run_bot_exchange_rates")
def run_bot_exchange_rate_scraper() -> dict[str, int | str | None]:
    scraper = BotExchangeRateScraper()
    try:
        return scraper.run()
    finally:
        scraper.close()
