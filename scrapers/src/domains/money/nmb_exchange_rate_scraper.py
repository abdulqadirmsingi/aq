"""NMB daily exchange-rate scraper."""

from __future__ import annotations

from src.core.config import load_settings
from src.core.fingerprint_store import DocumentFingerprintStore
from src.core.http_client import ScraperHttpClient
from src.domains.money.exchange_rate_scraper import ExchangeRateScraper
from src.domains.money.fx_persistence import ExchangeRatePersistenceStore
from src.domains.money.nmb_parser import (
    extract_latest_nmb_timestamp,
    infer_nmb_run_status,
    parse_nmb_daily_exchange_rates_html,
)


class NmbExchangeRateScraper(ExchangeRateScraper):
    name = "nmb_daily_exchange_rates"
    source_slug = "nmb_daily_exchange_rates"

    def __init__(
        self,
        http_client: ScraperHttpClient | None = None,
        *,
        listing_url: str | None = None,
    ) -> None:
        self._settings = load_settings()
        self._listing_url = listing_url or (
            "https://www.nmbbank.co.tz/treasury/foreign-exchange/nmb-daily-exchange-rates"
        )
        self._http = http_client or ScraperHttpClient(self._settings)
        self._should_close_client = http_client is None
        self._fingerprint_store: DocumentFingerprintStore | None = None
        self._owns_fingerprint_store = False
        persistence_store = None
        if self._settings.database_url:
            self._fingerprint_store = DocumentFingerprintStore(
                self._settings.database_url,
                self.source_slug,
            )
            self._owns_fingerprint_store = True
            persistence_store = ExchangeRatePersistenceStore(
                self._settings.database_url
            )
        super().__init__(persistence_store=persistence_store)

    def collect_observations(self):
        html = self._http.get_text(self._listing_url)
        return parse_nmb_daily_exchange_rates_html(html, source_url=self._listing_url)

    def run(self) -> dict[str, int | str | None]:
        html = self._http.get_text(self._listing_url)
        observations = parse_nmb_daily_exchange_rates_html(
            html,
            source_url=self._listing_url,
        )
        content_sha256 = (
            observations[0].ingestion_metadata.get("content_sha256")
            if observations
            else None
        )
        if (
            self._fingerprint_store is not None
            and content_sha256 is not None
            and self._fingerprint_store.has_successful_hash(str(content_sha256))
        ):
            self._fingerprint_store.upsert(
                document_url=self._listing_url,
                content_sha256=str(content_sha256),
                parse_ok=True,
                records_extracted=len(observations),
            )
            return {
                "attempted": len(observations),
                "inserted": 0,
                "updated": 0,
                "skipped": len(observations),
                "latest_timestamp": extract_latest_nmb_timestamp(observations),
            }

        if self._persistence_store is None:
            return {
                "attempted": len(observations),
                "inserted": 0,
                "updated": 0,
                "skipped": len(observations),
                "latest_timestamp": extract_latest_nmb_timestamp(observations),
            }

        run_id = self._persistence_store.start_run(
            scraper_name=self.name,
            source_slug=self.source_slug,
            trigger_type="scheduled",
        )
        try:
            result = self._persistence_store.persist_observations(
                observations,
                scraper_run_id=run_id,
            )
            if self._fingerprint_store is not None and content_sha256 is not None:
                self._fingerprint_store.upsert(
                    document_url=self._listing_url,
                    content_sha256=str(content_sha256),
                    parse_ok=True,
                    records_extracted=len(observations),
                )
            run_metadata = {
                "latest_timestamp": extract_latest_nmb_timestamp(observations),
                "source_url": self._listing_url,
            }
            self._persistence_store.finish_run(
                run_id,
                status=infer_nmb_run_status(observations),
                records_read=len(observations),
                records_inserted=result.inserted,
                records_updated=result.updated,
                records_rejected=0,
                run_metadata=run_metadata,
            )
            self._persistence_store.log_event(
                scraper_run_id=run_id,
                level="info",
                event_type="nmb_daily_exchange_rates_completed",
                message="NMB daily exchange-rate run completed.",
                details=run_metadata
                | {
                    "records_inserted": result.inserted,
                    "records_updated": result.updated,
                    "records_skipped": result.skipped,
                },
            )
            return {
                "attempted": len(observations),
                "inserted": result.inserted,
                "updated": result.updated,
                "skipped": result.skipped,
                "latest_timestamp": extract_latest_nmb_timestamp(observations),
            }
        except Exception as exc:
            self._persistence_store.finish_run(
                run_id,
                status="failed",
                records_read=len(observations),
                records_inserted=0,
                records_updated=0,
                records_rejected=len(observations),
                error_message=str(exc),
            )
            self._persistence_store.log_event(
                scraper_run_id=run_id,
                level="error",
                event_type="nmb_daily_exchange_rates_failed",
                message="NMB daily exchange-rate run failed.",
                details={"error": str(exc)},
            )
            raise

    def close(self) -> None:
        if self._should_close_client:
            self._http.close()
        if self._owns_fingerprint_store and self._fingerprint_store is not None:
            self._fingerprint_store.close()
        if self._persistence_store is not None:
            self._persistence_store.close()
