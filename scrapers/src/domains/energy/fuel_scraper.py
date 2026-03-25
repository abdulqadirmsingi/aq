"""Fuel price scrapers — EWURA cap prices (PDF + DOCX, in-memory)."""

from __future__ import annotations

import logging
from datetime import date

from src.core.base_scraper import BaseScraper
from src.core.config import load_settings
from src.core.fingerprint_store import DocumentFingerprintStore
from src.core.http_client import ScraperHttpClient
from src.domains.energy.ewura.document_pipeline import (
    download_cap_price_bulletin,
    parse_cap_price_bulletin_bytes,
)
from src.domains.energy.ewura.fetch import fetch_page
from src.domains.energy.ewura.listing import list_cap_price_documents_from_html
from src.domains.energy.ewura.models import EwuraParseOutcome, FilteredDocumentRef
from src.domains.energy.ewura.persistence import EwuraPersistenceStore, infer_run_status
from src.domains.energy.ewura.structured_log import ewura_info

logger = logging.getLogger(__name__)


class EwuraFuelScraper(BaseScraper):
    """Discover cap-price bulletins and parse PDF/DOCX in memory."""

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

    def fetch_and_parse_document(self, ref: FilteredDocumentRef) -> EwuraParseOutcome:
        """Download one PDF or DOCX in memory; return rows or a structured outcome."""
        step = download_cap_price_bulletin(
            self._http,
            ref,
            max_bytes=self._max_document_bytes(),
        )
        if isinstance(step, EwuraParseOutcome):
            return step
        raw, sha, ext = step
        return parse_cap_price_bulletin_bytes(raw, ext, ref, sha)

    def ingest_cap_price_documents(
        self,
        *,
        limit: int | None = None,
        fingerprint_store: DocumentFingerprintStore | None = None,
        persistence_store: EwuraPersistenceStore | None = None,
        scraper_run_id=None,
        source_id=None,
    ) -> list[EwuraParseOutcome]:
        """Parse listed PDF/DOCX bulletins; optional DB-backed dedupe."""
        self._last_inserted_count = 0
        refs = self.list_cap_price_documents()
        doc_refs = [
            r
            for r in refs
            if str(r.url)
            .lower()
            .split("?", maxsplit=1)[0]
            .endswith(
                (".pdf", ".docx"),
            )
        ]
        eff_limit = limit if limit is not None else self._settings.ewura_run_pdf_limit
        if eff_limit is not None:
            doc_refs = doc_refs[:eff_limit]

        outcomes: list[EwuraParseOutcome] = []
        for ref in doc_refs:
            url = str(ref.url)
            if (
                fingerprint_store
                and self._settings.ewura_skip_successful_urls
                and fingerprint_store.url_parse_succeeded(url)
            ):
                outcomes.append(
                    EwuraParseOutcome(
                        ok=False,
                        skipped=True,
                        document_url=url,
                        error="skipped_known_url",
                    ),
                )
                continue

            step = download_cap_price_bulletin(
                self._http,
                ref,
                max_bytes=self._max_document_bytes(),
            )
            if isinstance(step, EwuraParseOutcome):
                outcomes.append(step)
                continue
            raw, sha, ext = step

            if fingerprint_store and fingerprint_store.has_successful_hash(sha):
                fingerprint_store.upsert(
                    document_url=url,
                    content_sha256=sha,
                    parse_ok=True,
                    records_extracted=0,
                )
                outcomes.append(
                    EwuraParseOutcome(
                        ok=False,
                        skipped=True,
                        document_url=url,
                        error="skipped_duplicate_hash",
                    ),
                )
                continue

            outcome = parse_cap_price_bulletin_bytes(raw, ext, ref, sha)
            if self._should_skip_for_date_window(outcome):
                if fingerprint_store and outcome.payload is not None:
                    fingerprint_store.upsert(
                        document_url=url,
                        content_sha256=outcome.payload.content_sha256,
                        parse_ok=True,
                        records_extracted=0,
                    )
                outcomes.append(
                    EwuraParseOutcome(
                        ok=False,
                        skipped=True,
                        document_url=url,
                        payload=outcome.payload,
                        error="outside_date_window",
                    ),
                )
                continue
            if fingerprint_store and outcome.payload is not None:
                fingerprint_store.upsert(
                    document_url=url,
                    content_sha256=outcome.payload.content_sha256,
                    parse_ok=outcome.ok,
                    records_extracted=len(outcome.payload.data),
                )
            if (
                outcome.ok
                and outcome.payload
                and outcome.payload.data
                and persistence_store is not None
                and source_id is not None
            ):
                self._last_inserted_count += persistence_store.persist_payload(
                    outcome.payload,
                    scraper_run_id=scraper_run_id,
                    source_id=source_id,
                )
            outcomes.append(outcome)
        return outcomes

    def run(self) -> None:
        store: DocumentFingerprintStore | None = None
        own_store = False
        persistence_store: EwuraPersistenceStore | None = None
        run_id = None
        source_id = None
        if self._settings.database_url:
            store = DocumentFingerprintStore(
                self._settings.database_url,
                self.name,
            )
            own_store = True
            persistence_store = EwuraPersistenceStore(self._settings.database_url)
            run_id, source_id = persistence_store.start_run(trigger_type="scheduled")
        try:
            outcomes = self.ingest_cap_price_documents(
                fingerprint_store=store,
                persistence_store=persistence_store,
                scraper_run_id=run_id,
                source_id=source_id,
            )
            if persistence_store is not None and run_id is not None:
                persistence_store.finish_run(
                    run_id,
                    status=infer_run_status(outcomes),
                    records_read=sum(
                        len(o.payload.data)
                        for o in outcomes
                        if o.payload is not None
                    ),
                    records_inserted=self._last_inserted_count,
                    records_rejected=sum(1 for o in outcomes if not o.ok and not o.skipped),
                    run_metadata={
                        "documents_attempted": len(outcomes),
                        "documents_ok": sum(1 for o in outcomes if o.ok),
                        "documents_skipped": sum(1 for o in outcomes if o.skipped),
                    },
                )
        except Exception as exc:
            if persistence_store is not None and run_id is not None:
                persistence_store.finish_run(
                    run_id,
                    status="failed",
                    records_read=0,
                    records_inserted=0,
                    records_rejected=0,
                    error_message=str(exc),
                )
            raise
        finally:
            if own_store and store is not None:
                store.close()
            if persistence_store is not None:
                persistence_store.close()

        ok_n = sum(1 for o in outcomes if o.ok)
        skipped_n = sum(1 for o in outcomes if o.skipped)
        ewura_info(
            logger,
            "ewura_fuel_ingest_complete",
            event="ewura_fuel_ingest_complete",
            listing_url=self._listing_url,
            scraper=self.name,
            documents_attempted=len(outcomes),
            documents_ok=ok_n,
            documents_skipped=skipped_n,
        )

    def close(self) -> None:
        if self._should_close_client:
            self._http.close()

    def _should_skip_for_date_window(self, outcome: EwuraParseOutcome) -> bool:
        if outcome.payload is None or outcome.payload.published_date is None:
            return False
        published = date.fromisoformat(outcome.payload.published_date)
        return (
            published.year < self._settings.ewura_min_year
            or published.year > self._settings.ewura_max_year
        )
