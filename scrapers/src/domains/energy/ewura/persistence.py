"""Normalized EWURA persistence helpers for scraper runs and reference rows."""

from __future__ import annotations

import json
import re
import uuid
from collections.abc import Iterable
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from src.core.db_url import sync_database_url
from src.domains.energy.ewura.models import EwuraDocumentPayload

_EWURA_SOURCE_SLUG = "ewura"
_ENERGY_CATEGORY_SLUG = "energy"
_TZ_COUNTRY_PATH = "TZ"
_FUEL_METRICS: dict[str, tuple[str, str]] = {
    "petrol": (
        "ewura_petrol_cap_price",
        "Monthly EWURA retail cap price for petrol.",
    ),
    "diesel": (
        "ewura_diesel_cap_price",
        "Monthly EWURA retail cap price for diesel.",
    ),
    "kerosene": (
        "ewura_kerosene_cap_price",
        "Monthly EWURA retail cap price for kerosene.",
    ),
}
_TZ_REGION_SEEDS: tuple[tuple[str, str, str], ...] = (
    ("Arusha", "ARU", "TZ/arusha"),
    ("Dar es Salaam", "DSM", "TZ/dar-es-salaam"),
    ("Dodoma", "DOD", "TZ/dodoma"),
    ("Geita", "GET", "TZ/geita"),
    ("Iringa", "IRI", "TZ/iringa"),
    ("Kagera", "KAG", "TZ/kagera"),
    ("Katavi", "KTV", "TZ/katavi"),
    ("Kigoma", "KIG", "TZ/kigoma"),
    ("Kilimanjaro", "KIL", "TZ/kilimanjaro"),
    ("Lindi", "LIN", "TZ/lindi"),
    ("Manyara", "MNY", "TZ/manyara"),
    ("Mara", "MAR", "TZ/mara"),
    ("Mbeya", "MBY", "TZ/mbeya"),
    ("Mjini Magharibi", "MJM", "TZ/mjini-magharibi"),
    ("Morogoro", "MOR", "TZ/morogoro"),
    ("Mtwara", "MTW", "TZ/mtwara"),
    ("Mwanza", "MWZ", "TZ/mwanza"),
    ("Njombe", "NJO", "TZ/njombe"),
    ("Pemba North", "PNR", "TZ/pemba-north"),
    ("Pemba South", "PSR", "TZ/pemba-south"),
    ("Pwani", "PWA", "TZ/pwani"),
    ("Rukwa", "RKW", "TZ/rukwa"),
    ("Ruvuma", "RUV", "TZ/ruvuma"),
    ("Shinyanga", "SHY", "TZ/shinyanga"),
    ("Simiyu", "SIM", "TZ/simiyu"),
    ("Singida", "SIN", "TZ/singida"),
    ("Songwe", "SNG", "TZ/songwe"),
    ("Tabora", "TAB", "TZ/tabora"),
    ("Tanga", "TNG", "TZ/tanga"),
    ("Unguja North", "UNG-N", "TZ/unguja-north"),
    ("Unguja South", "UNG-S", "TZ/unguja-south"),
)


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unknown"


def _recorded_at_timestamp(value: date) -> datetime:
    return datetime(value.year, value.month, value.day, tzinfo=UTC)


def _external_reference(payload: EwuraDocumentPayload, fuel_type: str) -> str:
    return f"ewura:{fuel_type}:{payload.content_sha256[:48]}"


class EwuraPersistenceStore:
    """Persists EWURA observations into the normalized platform tables."""

    def __init__(self, database_url: str) -> None:
        self._engine: Engine = create_engine(
            sync_database_url(database_url),
            pool_pre_ping=True,
        )

    def close(self) -> None:
        self._engine.dispose()

    def ensure_reference_ids(self) -> tuple[UUID, UUID, UUID]:
        with self._engine.begin() as conn:
            return self._ensure_reference_ids(conn)

    def _ensure_reference_ids(self, conn: Connection) -> tuple[UUID, UUID, UUID]:
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
        self._ensure_region_locations(conn, country_id)
        return category_id, source_id, country_id

    def _ensure_region_locations(self, conn: Connection, country_id: UUID) -> None:
        for region_name, region_code, region_path in _TZ_REGION_SEEDS:
            conn.execute(
                text(
                    """
                    INSERT INTO locations (
                        id, name, code, level, parent_id, country_code, path,
                        is_active, created_at, updated_at
                    )
                    VALUES (
                        gen_random_uuid(), :name, :code, 'region', :parent_id, 'TZA', :path,
                        true, now(), now()
                    )
                    ON CONFLICT (path) DO UPDATE SET
                        name = EXCLUDED.name,
                        code = EXCLUDED.code,
                        level = EXCLUDED.level,
                        parent_id = EXCLUDED.parent_id,
                        updated_at = now()
                    """,
                ),
                {
                    "name": region_name,
                    "code": region_code,
                    "parent_id": country_id,
                    "path": region_path,
                },
            )

    def ensure_metric_ids(self) -> dict[str, UUID]:
        with self._engine.begin() as conn:
            category_id, source_id, _country_id = self._ensure_reference_ids(conn)
            return self._ensure_metric_ids(conn, category_id, source_id)

    def _ensure_metric_ids(
        self,
        conn: Connection,
        category_id: UUID,
        source_id: UUID,
    ) -> dict[str, UUID]:
        metric_ids: dict[str, UUID] = {}
        for fuel_type, (slug, description) in _FUEL_METRICS.items():
            metric_id = conn.execute(
                text(
                    """
                    INSERT INTO metrics (
                        id, slug, name, unit, description, category_id,
                        canonical_source_id, value_type, default_frequency,
                        is_location_required, validation_rules, dimensions_schema,
                        created_at, updated_at
                    )
                    VALUES (
                        gen_random_uuid(), :slug, :name, 'TZS/Litre', :description, :category_id,
                        :source_id, 'numeric', 'monthly',
                        true, CAST(:validation_rules AS jsonb),
                        CAST(:dimensions_schema AS jsonb),
                        now(), now()
                    )
                    ON CONFLICT (slug) DO UPDATE SET
                        name = EXCLUDED.name,
                        unit = EXCLUDED.unit,
                        description = EXCLUDED.description,
                        category_id = EXCLUDED.category_id,
                        canonical_source_id = EXCLUDED.canonical_source_id,
                        value_type = EXCLUDED.value_type,
                        default_frequency = EXCLUDED.default_frequency,
                        is_location_required = EXCLUDED.is_location_required,
                        validation_rules = EXCLUDED.validation_rules,
                        dimensions_schema = EXCLUDED.dimensions_schema,
                        updated_at = now()
                    RETURNING id
                    """,
                ),
                {
                    "slug": slug,
                    "name": f"EWURA {fuel_type.title()} Cap Price",
                    "description": description,
                    "category_id": category_id,
                    "source_id": source_id,
                    "validation_rules": json.dumps({"min": 0, "max": 100000}),
                    "dimensions_schema": json.dumps(
                        {
                            "fuel_type": {"type": "string"},
                            "document_url": {"type": "string"},
                        }
                    ),
                },
            ).scalar_one()
            metric_ids[fuel_type] = metric_id
        return metric_ids

    def start_run(self, *, trigger_type: str) -> tuple[UUID, UUID]:
        with self._engine.begin() as conn:
            category_id, source_id, _country_id = self._ensure_reference_ids(conn)
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

    def log_event(
        self,
        *,
        scraper_run_id: UUID,
        level: str,
        event_type: str,
        message: str,
        details: dict[str, object] | None = None,
        data_point_id: UUID | None = None,
        data_point_recorded_at: datetime | None = None,
    ) -> None:
        with self._engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO ingestion_logs (
                        id, scraper_run_id, data_point_id, data_point_recorded_at,
                        level, event_type, message, details, created_at
                    )
                    VALUES (
                        gen_random_uuid(), :scraper_run_id, :data_point_id, :data_point_recorded_at,
                        :level, :event_type, :message, CAST(:details AS jsonb), now()
                    )
                    """,
                ),
                {
                    "scraper_run_id": scraper_run_id,
                    "data_point_id": data_point_id,
                    "data_point_recorded_at": data_point_recorded_at,
                    "level": level,
                    "event_type": event_type,
                    "message": message,
                    "details": json.dumps(details or {}),
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

        inserted = 0
        with self._engine.begin() as conn:
            category_id, source_id, country_id = self._ensure_reference_ids(conn)
            metric_ids = self._ensure_metric_ids(conn, category_id, source_id)
            for rec in payload.data:
                location_id = self._resolve_location_id(conn, rec.location, country_id)
                inserted += self._upsert_datapoint(
                    conn,
                    payload=payload,
                    metric_id=metric_ids[rec.fuel_type],
                    location_id=location_id,
                    fuel_type=rec.fuel_type,
                    price=rec.price,
                    recorded_at=_recorded_at_timestamp(rec.recorded_at),
                    scraper_run_id=scraper_run_id,
                    source_id=source_id,
                    raw_location_text=rec.location,
                )
        return inserted

    def _resolve_location_id(
        self,
        conn: Connection,
        raw_location_text: str,
        country_id: UUID,
    ) -> UUID:
        region_name = self._infer_region_name(raw_location_text)
        if region_name is not None:
            region = conn.execute(
                text(
                    """
                    SELECT id, path
                    FROM locations
                    WHERE path = :path
                    LIMIT 1
                    """,
                ),
                {"path": f"{_TZ_COUNTRY_PATH}/{_slugify(region_name)}"},
            ).mappings().first()
            if region is not None:
                if raw_location_text.strip().casefold() == region_name.casefold():
                    return region["id"]

                child_path = f"{region['path']}/{_slugify(raw_location_text)}"
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
                            parent_id = EXCLUDED.parent_id,
                            updated_at = now()
                        RETURNING id
                        """,
                    ),
                    {
                        "name": raw_location_text,
                        "parent_id": region["id"],
                        "path": child_path,
                    },
                ).scalar_one()

        existing = conn.execute(
            text(
                """
                SELECT id
                FROM locations
                WHERE lower(name) = lower(:name)
                  AND country_code = 'TZA'
                ORDER BY
                  CASE level
                    WHEN 'city' THEN 1
                    WHEN 'district' THEN 2
                    WHEN 'ward' THEN 3
                    WHEN 'other' THEN 4
                    WHEN 'region' THEN 5
                    ELSE 6
                  END
                LIMIT 1
                """,
            ),
            {"name": raw_location_text},
        ).scalar_one_or_none()
        if existing is not None:
            return existing

        path = f"{_TZ_COUNTRY_PATH}/{_slugify(raw_location_text)}"
        existing = conn.execute(
            text(
                """
                SELECT id
                FROM locations
                WHERE path = :path
                LIMIT 1
                """,
            ),
            {"path": path},
        ).scalar_one_or_none()
        if existing is not None:
            return existing

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
                "name": raw_location_text,
                "parent_id": country_id,
                "path": path,
            },
        ).scalar_one()

    @staticmethod
    def _infer_region_name(raw_location_text: str) -> str | None:
        stripped = raw_location_text.strip()
        for region_name, _region_code, _region_path in _TZ_REGION_SEEDS:
            if stripped.casefold() == region_name.casefold():
                return region_name
            prefix = f"{region_name} ("
            if stripped.casefold().startswith(prefix.casefold()):
                return region_name
        return None

    def _upsert_datapoint(
        self,
        conn: Connection,
        *,
        payload: EwuraDocumentPayload,
        metric_id: UUID,
        location_id: UUID,
        fuel_type: str,
        price: int,
        recorded_at: datetime,
        scraper_run_id: UUID | None,
        source_id: UUID,
        raw_location_text: str,
    ) -> int:
        existing = conn.execute(
            text(
                """
                SELECT
                    dp.id,
                    dp.recorded_at,
                    dp.version_no,
                    dp.value_numeric,
                    dp.extra_data,
                    dp.ingestion_metadata
                FROM data_points AS dp
                WHERE dp.metric_id = :metric_id
                  AND dp.source_id = :source_id
                  AND dp.location_id = :location_id
                  AND dp.recorded_at = :recorded_at
                  AND dp.is_current = true
                LIMIT 1
                """,
            ),
            {
                "metric_id": metric_id,
                "source_id": source_id,
                "location_id": location_id,
                "recorded_at": recorded_at,
            },
        ).mappings().first()

        extra_data = {
            "document_url": payload.document_url,
            "published_date": payload.published_date,
            "raw_location_text": raw_location_text,
        }
        ingestion_metadata = {
            "content_sha256": payload.content_sha256,
            "source_label": payload.source,
            "parse_warnings": payload.parse_warnings,
        }

        if existing is not None:
            same_value = Decimal(str(price)) == existing["value_numeric"]
            same_extra = (existing["extra_data"] or {}) == extra_data
            same_ingestion = (existing["ingestion_metadata"] or {}) == ingestion_metadata
            if same_value and same_extra and same_ingestion:
                return 0

            conn.execute(
                text(
                    """
                    UPDATE data_points
                    SET
                        is_current = false
                    WHERE id = :id
                      AND recorded_at = :recorded_at
                    """,
                ),
                {
                    "id": existing["id"],
                    "recorded_at": existing["recorded_at"],
                },
            )
            version_no = int(existing["version_no"]) + 1
            supersedes_id = existing["id"]
            supersedes_recorded_at = existing["recorded_at"]
        else:
            version_no = 1
            supersedes_id = None
            supersedes_recorded_at = None

        data_point_id = uuid.uuid4()
        conn.execute(
            text(
                """
                INSERT INTO data_points (
                    id, metric_id, source_id, location_id, scraper_run_id,
                    supersedes_id, supersedes_recorded_at, external_reference,
                    unit_override, value_type, value_numeric, extra_data,
                    ingestion_metadata, recorded_at, version_no, is_current,
                    is_valid, confidence_score
                )
                VALUES (
                    :id, :metric_id, :source_id, :location_id, :scraper_run_id,
                    :supersedes_id, :supersedes_recorded_at, :external_reference,
                    :unit_override, 'numeric', :value_numeric, CAST(:extra_data AS jsonb),
                    CAST(:ingestion_metadata AS jsonb), :recorded_at, :version_no, true,
                    true, 1.0000
                )
                """,
            ),
            {
                "id": data_point_id,
                "metric_id": metric_id,
                "source_id": source_id,
                "location_id": location_id,
                "scraper_run_id": scraper_run_id,
                "supersedes_id": supersedes_id,
                "supersedes_recorded_at": supersedes_recorded_at,
                "external_reference": _external_reference(payload, fuel_type),
                "unit_override": "TZS/Litre",
                "value_numeric": str(price),
                "extra_data": json.dumps(extra_data),
                "ingestion_metadata": json.dumps(ingestion_metadata),
                "recorded_at": recorded_at,
                "version_no": version_no,
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO energy_details (
                    id, data_point_id, data_point_recorded_at, energy_type,
                    fuel_grade, provider_name, created_at, updated_at
                )
                VALUES (
                    gen_random_uuid(), :data_point_id, :recorded_at, 'fuel_cap_price',
                    :fuel_grade, 'EWURA', now(), now()
                )
                """,
            ),
            {
                "data_point_id": data_point_id,
                "recorded_at": recorded_at,
                "fuel_grade": fuel_type,
            },
        )
        return 1


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
