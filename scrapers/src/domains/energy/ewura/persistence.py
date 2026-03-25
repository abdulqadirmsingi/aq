"""Normalized EWURA persistence helpers for scraper runs and reference rows."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.core.db_url import sync_database_url
from src.domains.energy.ewura.models import EwuraDocumentPayload

_EWURA_SOURCE_SLUG = "ewura"
_ENERGY_CATEGORY_SLUG = "energy"
_TZ_COUNTRY_PATH = "TZ"


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unknown"


class EwuraPersistenceStore:
    """Persists EWURA observations while keeping reference tables in sync."""

    def __init__(self, database_url: str) -> None:
        self._engine: Engine = create_engine(
            sync_database_url(database_url),
            pool_pre_ping=True,
        )

    def close(self) -> None:
        self._engine.dispose()

    def ensure_reference_ids(self) -> tuple[UUID, UUID, UUID]:
        with self._engine.begin() as conn:
            category_id = conn.execute(
                text(
                    """
                    INSERT INTO data_categories (id, slug, name, description, created_at, updated_at)
                    VALUES (gen_random_uuid(), :slug, :name, :description, now(), now())
                    ON CONFLICT (slug) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        updated_at = now()
                    RETURNING id
                    """,
                ),
                {
                    "slug": _ENERGY_CATEGORY_SLUG,
                    "name": "Energy",
                    "description": "Energy market and tariff observations.",
                },
            ).scalar_one()
            source_id = conn.execute(
                text(
                    """
                    INSERT INTO sources (
                        id, slug, name, source_type, description, url,
                        reliability_score, metadata, created_at, updated_at
                    )
                    VALUES (
                        gen_random_uuid(), :slug, :name, 'government', :description, :url,
                        0.950, '{}'::jsonb, now(), now()
                    )
                    ON CONFLICT (slug) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        url = EXCLUDED.url,
                        updated_at = now()
                    RETURNING id
                    """,
                ),
                {
                    "slug": _EWURA_SOURCE_SLUG,
                    "name": "EWURA",
                    "description": "Energy and Water Utilities Regulatory Authority petroleum cap prices.",
                    "url": "https://www.ewura.go.tz/pages/petroleum-product-pricing",
                },
            ).scalar_one()
            country_id = conn.execute(
                text(
                    """
                    INSERT INTO locations (
                        id, name, code, level, parent_id, country_code, path,
                        is_active, created_at, updated_at
                    )
                    VALUES (
                        gen_random_uuid(), 'Tanzania', 'TZ', 'country', NULL, 'TZA', :path,
                        true, now(), now()
                    )
                    ON CONFLICT (path) DO UPDATE SET
                        name = EXCLUDED.name,
                        code = EXCLUDED.code,
                        country_code = EXCLUDED.country_code,
                        updated_at = now()
                    RETURNING id
                    """,
                ),
                {"path": _TZ_COUNTRY_PATH},
            ).scalar_one()
        return category_id, source_id, country_id

    def start_run(self, *, trigger_type: str) -> tuple[UUID, UUID]:
        category_id, source_id, _country_id = self.ensure_reference_ids()
        with self._engine.begin() as conn:
            run_id = conn.execute(
                text(
                    """
                    INSERT INTO scraper_runs (
                        id, scraper_name, trigger_type, status, category_id, source_id,
                        started_at, run_metadata, created_at, updated_at
                    )
                    VALUES (
                        gen_random_uuid(), :scraper_name, :trigger_type, 'running', :category_id, :source_id,
                        now(), '{}'::jsonb, now(), now()
                    )
                    RETURNING id
                    """,
                ),
                {
                    "scraper_name": "ewura_fuel",
                    "trigger_type": trigger_type,
                    "category_id": category_id,
                    "source_id": source_id,
                },
            ).scalar_one()
        return run_id, source_id

    def finish_run(
        self,
        run_id: UUID,
        *,
        status: str,
        records_read: int,
        records_inserted: int,
        records_rejected: int,
        error_message: str | None = None,
        run_metadata: dict[str, object] | None = None,
    ) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    """
                    UPDATE scraper_runs
                    SET
                        status = :status,
                        finished_at = now(),
                        records_read = :records_read,
                        records_inserted = :records_inserted,
                        records_rejected = :records_rejected,
                        error_message = :error_message,
                        run_metadata = CAST(:run_metadata AS jsonb),
                        updated_at = now()
                    WHERE id = :run_id
                    """,
                ),
                {
                    "run_id": run_id,
                    "status": status,
                    "records_read": records_read,
                    "records_inserted": records_inserted,
                    "records_rejected": records_rejected,
                    "error_message": error_message,
                    "run_metadata": "{}" if run_metadata is None else json.dumps(run_metadata),
                },
            )

    def persist_payload(
        self,
        payload: EwuraDocumentPayload,
        *,
        scraper_run_id: UUID | None,
        source_id: UUID,
    ) -> int:
        if not payload.data:
            return 0

        country_id = self.ensure_reference_ids()[2]
        payload.source_id = source_id
        published_date = payload.published_date
        sql = text(
            """
            INSERT INTO ewura_fuel_observations (
                source_id, scraper_run_id, location_id, source_label,
                document_url, content_sha256, published_date,
                location, fuel_type, price, unit, recorded_at
            ) VALUES (
                :source_id, :scraper_run_id, :location_id, :source_label,
                :document_url, :sha, :published_date,
                :location, :fuel_type, :price, :unit, :recorded_at
            )
            ON CONFLICT (content_sha256, location, fuel_type, recorded_at) DO NOTHING
            """,
        )
        inserted = 0
        with self._engine.begin() as conn:
            for rec in payload.data:
                location_id = self._ensure_location(conn, rec.location, country_id)
                res = conn.execute(
                    sql,
                    {
                        "source_id": source_id,
                        "scraper_run_id": scraper_run_id,
                        "location_id": location_id,
                        "source_label": payload.source,
                        "document_url": payload.document_url,
                        "sha": payload.content_sha256,
                        "published_date": published_date,
                        "location": rec.location,
                        "fuel_type": rec.fuel_type,
                        "price": rec.price,
                        "unit": rec.unit,
                        "recorded_at": rec.recorded_at,
                    },
                )
                if res.rowcount:
                    inserted += res.rowcount
        return inserted

    def _ensure_location(self, conn, name: str, country_id: UUID) -> UUID:
        path = f"{_TZ_COUNTRY_PATH}/{_slugify(name)}"
        return conn.execute(
            text(
                """
                INSERT INTO locations (
                    id, name, level, parent_id, country_code, path,
                    is_active, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :name, 'other', :parent_id, 'TZA', :path,
                    true, now(), now()
                )
                ON CONFLICT (path) DO UPDATE SET
                    name = EXCLUDED.name,
                    updated_at = now()
                RETURNING id
                """,
            ),
            {
                "name": name,
                "parent_id": country_id,
                "path": path,
            },
        ).scalar_one()


def infer_run_status(outcomes: Iterable[object]) -> str:
    ok = 0
    failed = 0
    for outcome in outcomes:
        if getattr(outcome, "ok", False):
            ok += 1
        elif not getattr(outcome, "skipped", False):
            failed += 1
    if failed and ok:
        return "partial"
    if failed:
        return "failed"
    return "succeeded"
