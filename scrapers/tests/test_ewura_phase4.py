"""Phase 4: DB URL helper, Celery registration, fingerprint hooks (no live Postgres)."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from unittest.mock import MagicMock

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
