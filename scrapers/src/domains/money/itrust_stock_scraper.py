"""iTrust DSE market-summary scraper."""

from __future__ import annotations

from src.core.config import load_settings
from src.core.fingerprint_store import DocumentFingerprintStore
from src.core.http_client import ScraperHttpClient
from src.domains.money.itrust_parser import SUMMARY_URL, parse_itrust_market_summary
from src.domains.money.stock_persistence import StockPersistenceStore


class ItrustStockScraper:
    """Fetch the iTrust DSE market-summary API and persist OHLCV observations."""

    name = "itrust_dse"
    source_slug = "itrust_dse"

    def __init__(
        self,
        http_client: ScraperHttpClient | None = None,
        *,
        summary_url: str | None = None,
    ) -> None:
        self._settings = load_settings()
        self._summary_url = summary_url or SUMMARY_URL
        self._http = http_client or ScraperHttpClient(self._settings)
        self._should_close_client = http_client is None
        self._fingerprint_store: DocumentFingerprintStore | None = None
        self._owns_fingerprint_store = False
        self._persistence_store: StockPersistenceStore | None = None

        if self._settings.database_url:
            self._fingerprint_store = DocumentFingerprintStore(
                self._settings.database_url,
                self.source_slug,
            )
            self._owns_fingerprint_store = True
            self._persistence_store = StockPersistenceStore(self._settings.database_url)

    def close(self) -> None:
        if self._should_close_client:
            self._http.close()
        if self._owns_fingerprint_store and self._fingerprint_store is not None:
            self._fingerprint_store.close()
        if self._persistence_store is not None:
            self._persistence_store.close()

    def run(self) -> dict[str, int | str | None]:
        raw_json = self._http.get_text(self._summary_url)
        observations = parse_itrust_market_summary(
            raw_json, source_url=self._summary_url
        )

        content_sha256 = (
            observations[0].ingestion_metadata.get("content_sha256")
            if observations
            else None
        )

        # Dedupe: if we've successfully ingested this exact payload before, skip.
        if (
            self._fingerprint_store is not None
            and content_sha256 is not None
            and self._fingerprint_store.has_successful_hash(str(content_sha256))
        ):
            return {
                "attempted": len(observations),
                "inserted": 0,
                "updated": 0,
                "skipped": len(observations),
                "trade_date": observations[0].detail.trade_date.isoformat()
                if observations
                else None,
            }

        if self._persistence_store is None:
            return {
                "attempted": len(observations),
                "inserted": 0,
                "updated": 0,
                "skipped": len(observations),
                "trade_date": observations[0].detail.trade_date.isoformat()
                if observations
                else None,
            }

        trade_date = (
            observations[0].detail.trade_date.isoformat() if observations else None
        )
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
                    document_url=self._summary_url,
                    content_sha256=str(content_sha256),
                    parse_ok=True,
                    records_extracted=len(observations),
                )
            run_metadata = {
                "trade_date": trade_date,
                "source_url": self._summary_url,
            }
            self._persistence_store.finish_run(
                run_id,
                status="succeeded",
                records_read=len(observations),
                records_inserted=result.inserted,
                records_updated=result.updated,
                records_rejected=0,
                run_metadata=run_metadata,
            )
            self._persistence_store.log_event(
                scraper_run_id=run_id,
                level="info",
                event_type="itrust_dse_completed",
                message="iTrust DSE stock scraper run completed.",
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
                "trade_date": trade_date,
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
                event_type="itrust_dse_failed",
                message="iTrust DSE stock scraper run failed.",
                details={"error": str(exc)},
            )
            raise
