"""Celery task definitions — domain scrapers."""

from __future__ import annotations

import httpx

from src.domains.energy.fuel_scraper import EwuraFuelScraper
from src.domains.money.bot_exchange_rate_scraper import BotExchangeRateScraper
from src.domains.money.crdb_exchange_rate_scraper import CrdbExchangeRateScraper
from src.domains.money.itrust_stock_scraper import ItrustStockScraper
from src.domains.money.nmb_exchange_rate_scraper import NmbExchangeRateScraper
from src.domains.procurement.scraper import NestProcurementScraper
from src.workers.celery_app import app


@app.task(
    name="scrapers.run_ewura_fuel",
    autoretry_for=(httpx.TimeoutException, httpx.TransportError),
    retry_backoff=900,
    retry_backoff_max=21_600,
    retry_jitter=True,
    max_retries=3,
)
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


@app.task(name="scrapers.run_crdb_forex")
def run_crdb_exchange_rate_scraper() -> dict[str, int | str | None]:
    scraper = CrdbExchangeRateScraper()
    try:
        return scraper.run()
    finally:
        scraper.close()


@app.task(name="scrapers.run_nmb_daily_exchange_rates")
def run_nmb_exchange_rate_scraper() -> dict[str, int | str | None]:
    scraper = NmbExchangeRateScraper()
    try:
        return scraper.run()
    finally:
        scraper.close()


@app.task(
    name="scrapers.run_itrust_dse_stocks",
    autoretry_for=(httpx.TimeoutException, httpx.TransportError),
    retry_backoff=60,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
)
def run_itrust_stock_scraper() -> dict[str, int | str | None]:
    """Fetch the iTrust DSE market-summary API and persist daily OHLCV records."""
    scraper = ItrustStockScraper()
    try:
        return scraper.run()
    finally:
        scraper.close()


@app.task(
    name="scrapers.run_nest_procurement",
    autoretry_for=(httpx.TimeoutException, httpx.TransportError),
    retry_backoff=300,
    retry_backoff_max=3600,
    retry_jitter=True,
    max_retries=3,
)
def run_nest_procurement_scraper() -> dict[str, int]:
    """Fetch all OCDS records from data.nest.go.tz and upsert procurement_tenders."""
    scraper = NestProcurementScraper()
    try:
        return scraper.run()
    finally:
        scraper.close()
