"""Persistence store for NeST procurement tenders."""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from src.core.db_url import sync_database_url
from src.domains.procurement.constants import (
    NEST_SOURCE_SLUG,
    PROCUREMENT_CATEGORY_SLUG,
)
from src.domains.procurement.models import NormalizedTender, PersistResult
from src.domains.procurement.persistence_bootstrap import ensure_reference_ids


class NestProcurementPersistenceStore:
    """Upsert normalized tenders into procurement_tenders; track runs in scraper_runs."""

    def __init__(self, database_url: str) -> None:
        self._engine: Engine = create_engine(
            sync_database_url(database_url),
            pool_pre_ping=True,
        )

    def close(self) -> None:
        self._engine.dispose()

    def __enter__(self) -> NestProcurementPersistenceStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def start_run(self, *, scraper_name: str, trigger_type: str) -> UUID:
        with self._engine.begin() as conn:
            refs = ensure_reference_ids(conn)
            run_id = conn.execute(
                text(
                    """
                    INSERT INTO scraper_runs (
                        id, scraper_name, trigger_type, status,
                        category_id, source_id, started_at,
                        run_metadata, created_at, updated_at
                    )
                    VALUES (
                        :id, :scraper_name, :trigger_type, 'running',
                        :category_id, :source_id, now(),
                        '{}'::jsonb, now(), now()
                    )
                    RETURNING id
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "scraper_name": scraper_name,
                    "trigger_type": trigger_type,
                    "category_id": refs[PROCUREMENT_CATEGORY_SLUG],
                    "source_id": refs[NEST_SOURCE_SLUG],
                },
            ).scalar_one()
        return run_id

    def finish_run(
        self,
        run_id: UUID,
        *,
        status: str,
        records_read: int,
        records_inserted: int,
        records_updated: int,
        records_rejected: int,
        error_message: str | None = None,
        run_metadata: dict[str, object] | None = None,
    ) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE scraper_runs
                    SET status = :status, finished_at = now(),
                        records_read = :records_read,
                        records_inserted = :records_inserted,
                        records_updated = :records_updated,
                        records_rejected = :records_rejected,
                        error_message = :error_message,
                        run_metadata = CAST(:run_metadata AS jsonb),
                        updated_at = now()
                    WHERE id = :run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "status": status,
                    "records_read": records_read,
                    "records_inserted": records_inserted,
                    "records_updated": records_updated,
                    "records_rejected": records_rejected,
                    "error_message": error_message,
                    "run_metadata": json.dumps(run_metadata or {}),
                },
            )

    def upsert_tenders(
        self,
        tenders: Iterable[NormalizedTender],
        *,
        scraper_run_id: UUID | None = None,
    ) -> PersistResult:
        result = PersistResult()
        with self._engine.begin() as conn:
            for tender in tenders:
                result += _upsert_single(conn, tender)
        return result


def _upsert_single(conn: Connection, tender: NormalizedTender) -> PersistResult:
    existing = conn.execute(
        text(
            "SELECT raw_ocds_fingerprint FROM procurement_tenders WHERE ocid = :ocid LIMIT 1"
        ),
        {"ocid": tender.ocid},
    ).mappings().first()

    if existing is not None:
        if existing["raw_ocds_fingerprint"] == tender.raw_ocds_fingerprint:
            return PersistResult(skipped=1)
        conn.execute(text(_UPDATE_SQL), _params(tender))
        return PersistResult(updated=1)

    conn.execute(text(_INSERT_SQL), {"id": uuid.uuid4(), **_params(tender)})
    return PersistResult(inserted=1)


_UPDATE_SQL = """
UPDATE procurement_tenders SET
    tender_reference = :tender_reference, title = :title,
    description = :description,
    procuring_entity_name = :procuring_entity_name,
    procuring_entity_id = :procuring_entity_id,
    procurement_method = :procurement_method,
    procurement_method_details = :procurement_method_details,
    tender_status = :tender_status,
    tender_value_amount = :tender_value_amount,
    tender_value_currency = :tender_value_currency,
    tender_period_start = :tender_period_start,
    tender_period_end = :tender_period_end,
    has_award = :has_award, award_date = :award_date,
    award_value_amount = :award_value_amount,
    award_value_currency = :award_value_currency,
    contractor_name = :contractor_name, contractor_id = :contractor_id,
    financial_year = :financial_year, location = :location,
    raw_ocds = CAST(:raw_ocds AS jsonb),
    raw_ocds_fingerprint = :raw_ocds_fingerprint,
    source_url = :source_url, fetched_at = now(), updated_at = now()
WHERE ocid = :ocid
"""

_INSERT_SQL = """
INSERT INTO procurement_tenders (
    id, ocid, tender_reference, title, description,
    procuring_entity_name, procuring_entity_id,
    procurement_method, procurement_method_details,
    tender_status, tender_value_amount, tender_value_currency,
    tender_period_start, tender_period_end,
    has_award, award_date, award_value_amount, award_value_currency,
    contractor_name, contractor_id, financial_year, location,
    raw_ocds, raw_ocds_fingerprint, source_url,
    fetched_at, created_at, updated_at
)
VALUES (
    :id, :ocid, :tender_reference, :title, :description,
    :procuring_entity_name, :procuring_entity_id,
    :procurement_method, :procurement_method_details,
    :tender_status, :tender_value_amount, :tender_value_currency,
    :tender_period_start, :tender_period_end,
    :has_award, :award_date, :award_value_amount, :award_value_currency,
    :contractor_name, :contractor_id, :financial_year, :location,
    CAST(:raw_ocds AS jsonb), :raw_ocds_fingerprint, :source_url,
    now(), now(), now()
)
"""


def _params(tender: NormalizedTender) -> dict[str, object]:
    return {
        "ocid": tender.ocid,
        "tender_reference": tender.tender_reference,
        "title": tender.title,
        "description": tender.description,
        "procuring_entity_name": tender.procuring_entity_name,
        "procuring_entity_id": tender.procuring_entity_id,
        "procurement_method": tender.procurement_method,
        "procurement_method_details": tender.procurement_method_details,
        "tender_status": tender.tender_status,
        "tender_value_amount": tender.tender_value_amount,
        "tender_value_currency": tender.tender_value_currency,
        "tender_period_start": tender.tender_period_start,
        "tender_period_end": tender.tender_period_end,
        "has_award": tender.has_award,
        "award_date": tender.award_date,
        "award_value_amount": tender.award_value_amount,
        "award_value_currency": tender.award_value_currency,
        "contractor_name": tender.contractor_name,
        "contractor_id": tender.contractor_id,
        "financial_year": tender.financial_year,
        "location": tender.location,
        "raw_ocds": json.dumps(tender.raw_ocds, default=str),
        "raw_ocds_fingerprint": tender.raw_ocds_fingerprint,
        "source_url": tender.source_url,
    }
