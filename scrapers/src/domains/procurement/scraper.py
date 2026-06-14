"""NeST PPRA procurement scraper — fetches OCDS records and persists tenders."""

from __future__ import annotations

import logging

from src.core.base_scraper import BaseScraper
from src.core.config import load_settings
from src.domains.procurement.api_client import NestOcdsApiClient
from src.domains.procurement.parser import parse_ocds_record
from src.domains.procurement.persistence import NestProcurementPersistenceStore

logger = logging.getLogger(__name__)


class NestProcurementScraper(BaseScraper):
    """Fetch all OCDS records from data.nest.go.tz and upsert into procurement_tenders."""

    name = "nest_procurement"

    def __init__(self) -> None:
        self._settings = load_settings()
        self._api = NestOcdsApiClient(
            base_url=self._settings.nest_ocds_api_url,
            timeout=self._settings.http_timeout_seconds,
        )
        self._persistence: NestProcurementPersistenceStore | None = None
        if self._settings.database_url:
            self._persistence = NestProcurementPersistenceStore(
                self._settings.database_url
            )

    def run(self) -> dict[str, int]:
        raw_records = self._api.fetch_all_records()
        tenders = [
            t
            for r in raw_records
            if (t := parse_ocds_record(r, source_url=self._settings.nest_ocds_api_url))
            is not None
        ]
        rejected = len(raw_records) - len(tenders)
        logger.info(
            "Parsed %d/%d OCDS records (rejected: %d)",
            len(tenders),
            len(raw_records),
            rejected,
        )

        if self._persistence is None:
            return {
                "attempted": len(tenders),
                "inserted": 0,
                "updated": 0,
                "skipped": len(tenders),
                "rejected": rejected,
            }

        run_id = self._persistence.start_run(
            scraper_name=self.name,
            trigger_type="scheduled",
        )
        try:
            result = self._persistence.upsert_tenders(
                tenders,
                scraper_run_id=run_id,
            )
            self._persistence.finish_run(
                run_id,
                status="succeeded",
                records_read=len(raw_records),
                records_inserted=result.inserted,
                records_updated=result.updated,
                records_rejected=rejected,
                run_metadata={
                    "total_raw": len(raw_records),
                    "parsed": len(tenders),
                    "inserted": result.inserted,
                    "updated": result.updated,
                    "skipped": result.skipped,
                    "rejected": rejected,
                },
            )
            return {
                "attempted": len(tenders),
                "inserted": result.inserted,
                "updated": result.updated,
                "skipped": result.skipped,
                "rejected": rejected,
            }
        except Exception as exc:
            self._persistence.finish_run(
                run_id,
                status="failed",
                records_read=len(raw_records),
                records_inserted=0,
                records_updated=0,
                records_rejected=len(raw_records),
                error_message=str(exc),
            )
            raise

    def close(self) -> None:
        self._api.close()
        if self._persistence is not None:
            self._persistence.close()
