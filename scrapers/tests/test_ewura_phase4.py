"""Phase 4: DB URL helper, Celery registration, fingerprint hooks (no live Postgres)."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx

from src.core.db_url import sync_database_url
from src.domains.energy.ewura.models import EwuraParseOutcome, FilteredDocumentRef
from src.domains.energy.fuel_scraper import EwuraFuelScraper


def test_sync_database_url_asyncpg_to_psycopg() -> None:
    u = "postgresql+asyncpg://u:p@localhost:5432/db"
    assert sync_database_url(u) == "postgresql+psycopg://u:p@localhost:5432/db"


def test_sync_database_url_idempotent_psycopg() -> None:
    u = "postgresql+psycopg://u:p@localhost:5432/db"
    assert sync_database_url(u) == u


def test_ewura_parse_outcome_skipped_default() -> None:
    o = EwuraParseOutcome(ok=True, document_url="https://x/y.pdf")
    assert o.skipped is False


def test_celery_registers_ewura_task() -> None:
    importlib.import_module("src.workers.tasks")
    from src.workers.celery_app import app

    assert "scrapers.run_ewura_fuel" in app.tasks


def test_celery_ewura_task_retries_transient_http_failures() -> None:
    importlib.import_module("src.workers.tasks")
    from src.workers.tasks import run_ewura_fuel_scraper

    assert run_ewura_fuel_scraper.autoretry_for == (
        httpx.TimeoutException,
        httpx.TransportError,
    )
    assert run_ewura_fuel_scraper.retry_backoff == 900
    assert run_ewura_fuel_scraper.retry_backoff_max == 21_600
    assert run_ewura_fuel_scraper.retry_jitter is True


def test_ingest_skips_known_url_when_store_says_so() -> None:
    store = MagicMock()
    store.url_parse_succeeded.return_value = True
    store.has_successful_hash.return_value = False

    scraper = MagicMock()
    scraper._settings = SimpleNamespace(
        ewura_skip_successful_urls=True,
        ewura_run_pdf_limit=None,
    )
    scraper._max_document_bytes = lambda: 10_000_000
    scraper.list_cap_price_documents.return_value = [
        FilteredDocumentRef(
            url="https://www.ewura.go.tz/uploads/documents/a.pdf",
            link_text="Cap Prices",
        ),
    ]

    outcomes = EwuraFuelScraper.ingest_cap_price_documents(
        scraper,
        fingerprint_store=store,
    )
    assert len(outcomes) == 1
    assert outcomes[0].skipped is True
    assert outcomes[0].error == "skipped_known_url"
    scraper._http.assert_not_called()


def test_ingest_skips_out_of_window_payload() -> None:
    scraper = MagicMock()
    scraper._settings = SimpleNamespace(
        ewura_skip_successful_urls=False,
        ewura_run_pdf_limit=None,
        ewura_min_year=2025,
        ewura_max_year=2026,
    )
    scraper._max_document_bytes = lambda: 10_000_000
    scraper.list_cap_price_documents.return_value = [
        FilteredDocumentRef(
            url="https://www.ewura.go.tz/uploads/documents/a.pdf",
            link_text="Cap Prices",
        ),
    ]
    scraper._should_skip_for_date_window = EwuraFuelScraper._should_skip_for_date_window.__get__(
        scraper,
        EwuraFuelScraper,
    )

    from src.domains.energy.ewura.models import EwuraDocumentPayload

    payload = EwuraDocumentPayload(
        document_url="https://www.ewura.go.tz/uploads/documents/a.pdf",
        published_date="2024-12-01",
        data=[],
        content_sha256="c" * 64,
    )

    import src.domains.energy.fuel_scraper as fuel_scraper_module

    original_download = fuel_scraper_module.download_cap_price_bulletin
    original_parse = fuel_scraper_module.parse_cap_price_bulletin_bytes
    fuel_scraper_module.download_cap_price_bulletin = MagicMock(
        return_value=(b"pdf", "c" * 64, ".pdf")
    )
    fuel_scraper_module.parse_cap_price_bulletin_bytes = MagicMock(
        return_value=EwuraParseOutcome(
            ok=False,
            document_url="https://www.ewura.go.tz/uploads/documents/a.pdf",
            payload=payload,
        )
    )
    try:
        outcomes = EwuraFuelScraper.ingest_cap_price_documents(scraper)
    finally:
        fuel_scraper_module.download_cap_price_bulletin = original_download
        fuel_scraper_module.parse_cap_price_bulletin_bytes = original_parse

    assert len(outcomes) == 1
    assert outcomes[0].skipped is True
    assert outcomes[0].error == "outside_date_window"
