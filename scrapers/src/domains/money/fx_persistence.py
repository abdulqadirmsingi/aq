"""Shared persistence helpers for normalized exchange-rate scraper outputs."""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterable
from datetime import datetime
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from src.core.db_url import sync_database_url
from src.domains.money.constants import (
    EXCHANGE_RATE_METRICS,
    EXCHANGE_RATE_SOURCES,
    MONEY_CATEGORY_DESCRIPTION,
    MONEY_CATEGORY_NAME,
    MONEY_CATEGORY_SLUG,
    TANZANIA_COUNTRY_CODE,
    TANZANIA_COUNTRY_CODE_ALPHA3,
    TANZANIA_COUNTRY_NAME,
    TANZANIA_LOCATION_PATH,
)
from src.domains.money.fx_models import (
    NormalizedFxObservation,
    PersistObservationResult,
)
from src.domains.money.fx_utils import payload_fingerprint


class ExchangeRatePersistenceStore:
    """Persist normalized FX observations into the shared platform tables."""

    def __init__(self, database_url: str) -> None:
        self._engine: Engine = create_engine(
            sync_database_url(database_url),
            pool_pre_ping=True,
        )

    def close(self) -> None:
        self._engine.dispose()

    def __enter__(self) -> ExchangeRatePersistenceStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def ensure_reference_ids(self) -> dict[str, UUID]:
        with self._engine.begin() as conn:
            return self._ensure_reference_ids(conn)

    def start_run(
        self,
        *,
        scraper_name: str,
        source_slug: str,
        trigger_type: str,
    ) -> UUID:
        with self._engine.begin() as conn:
            references = self._ensure_reference_ids(conn)
            run_id = conn.execute(
                text(
                    """
                    INSERT INTO scraper_runs (
                        id, scraper_name, trigger_type, status, category_id, source_id,
                        started_at, run_metadata, created_at, updated_at
                    )
                    VALUES (
                        :id, :scraper_name, :trigger_type, 'running',
                        :category_id, :source_id,
                        now(), '{}'::jsonb, now(), now()
                    )
                    RETURNING id
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "scraper_name": scraper_name,
                    "trigger_type": trigger_type,
                    "category_id": references[MONEY_CATEGORY_SLUG],
                    "source_id": references[source_slug],
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
                    SET
                        status = :status,
                        finished_at = now(),
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
                        :id, :scraper_run_id, :data_point_id, :data_point_recorded_at,
                        :level, :event_type, :message, CAST(:details AS jsonb), now()
                    )
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "scraper_run_id": scraper_run_id,
                    "data_point_id": data_point_id,
                    "data_point_recorded_at": data_point_recorded_at,
                    "level": level,
                    "event_type": event_type,
                    "message": message,
                    "details": json.dumps(details or {}),
                },
            )

    def persist_observations(
        self,
        observations: Iterable[NormalizedFxObservation],
        *,
        scraper_run_id: UUID | None = None,
    ) -> PersistObservationResult:
        result = PersistObservationResult()
        observation_list = list(observations)
        if not observation_list:
            return result

        with self._engine.begin() as conn:
            references = self._ensure_reference_ids(conn)
            for observation in observation_list:
                result += self._persist_single_observation(
                    conn,
                    observation=observation,
                    references=references,
                    scraper_run_id=scraper_run_id,
                )
        return result

    def _ensure_reference_ids(self, conn: Connection) -> dict[str, UUID]:
        references: dict[str, UUID] = {}
        category_id = conn.execute(
            text(
                """
                INSERT INTO data_categories (
                    id, slug, name, description, config, created_at, updated_at
                )
                VALUES (
                    :id, :slug, :name, :description, '{}'::jsonb, now(), now()
                )
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    updated_at = now()
                RETURNING id
                """
            ),
            {
                "id": uuid.uuid4(),
                "slug": MONEY_CATEGORY_SLUG,
                "name": MONEY_CATEGORY_NAME,
                "description": MONEY_CATEGORY_DESCRIPTION,
            },
        ).scalar_one()
        references[MONEY_CATEGORY_SLUG] = category_id

        tanzania_id = conn.execute(
            text(
                """
                INSERT INTO locations (
                    id, name, code, level, parent_id, country_code, path,
                    is_active, created_at, updated_at
                )
                VALUES (
                    :id, :name, :code, 'country', NULL, :country_code, :path,
                    true, now(), now()
                )
                ON CONFLICT (path) DO UPDATE SET
                    name = EXCLUDED.name,
                    code = EXCLUDED.code,
                    country_code = EXCLUDED.country_code,
                    updated_at = now()
                RETURNING id
                """
            ),
            {
                "id": uuid.uuid4(),
                "name": TANZANIA_COUNTRY_NAME,
                "code": TANZANIA_COUNTRY_CODE,
                "country_code": TANZANIA_COUNTRY_CODE_ALPHA3,
                "path": TANZANIA_LOCATION_PATH,
            },
        ).scalar_one()
        references[TANZANIA_LOCATION_PATH] = tanzania_id

        for source in EXCHANGE_RATE_SOURCES:
            source_id = conn.execute(
                text(
                    """
                    INSERT INTO sources (
                        id, slug, name, source_type, description, url,
                        reliability_score,
                        is_active, metadata, created_at, updated_at
                    )
                    VALUES (
                        :id, :slug, :name, :source_type, :description, :url,
                        :reliability_score,
                        true, '{}'::jsonb, now(), now()
                    )
                    ON CONFLICT (slug) DO UPDATE SET
                        name = EXCLUDED.name,
                        source_type = EXCLUDED.source_type,
                        description = EXCLUDED.description,
                        url = EXCLUDED.url,
                        reliability_score = EXCLUDED.reliability_score,
                        updated_at = now()
                    RETURNING id
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "slug": source.slug,
                    "name": source.name,
                    "source_type": source.source_type,
                    "description": source.description,
                    "url": source.url,
                    "reliability_score": source.reliability_score,
                },
            ).scalar_one()
            references[source.slug] = source_id

        for metric in EXCHANGE_RATE_METRICS:
            metric_id = conn.execute(
                text(
                    """
                    INSERT INTO metrics (
                        id, slug, name, unit, description, category_id,
                        canonical_source_id, value_type, default_frequency,
                        is_location_required, validation_rules,
                        dimensions_schema, created_at, updated_at
                    )
                    VALUES (
                        :id, :slug, :name, 'TZS', :description, :category_id, NULL,
                        'numeric', 'daily', false, CAST(:validation_rules AS jsonb),
                        CAST(:dimensions_schema AS jsonb), now(), now()
                    )
                    ON CONFLICT (slug) DO UPDATE SET
                        name = EXCLUDED.name,
                        unit = EXCLUDED.unit,
                        description = EXCLUDED.description,
                        category_id = EXCLUDED.category_id,
                        value_type = EXCLUDED.value_type,
                        default_frequency = EXCLUDED.default_frequency,
                        dimensions_schema = EXCLUDED.dimensions_schema,
                        updated_at = now()
                    RETURNING id
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "slug": metric.slug,
                    "name": metric.name,
                    "description": metric.description,
                    "category_id": category_id,
                    "validation_rules": json.dumps({"minimum": 0}),
                    "dimensions_schema": json.dumps(
                        {
                            "instrument_code": {"type": "string"},
                            "quote_code": {"type": "string"},
                            "market_scope": {"type": "string"},
                            "channel": {"type": ["string", "null"]},
                            "cash_note_band": {"type": ["string", "null"]},
                            "source_effective_date": {"type": ["string", "null"]},
                            "source_last_updated_at": {"type": ["string", "null"]},
                        }
                    ),
                },
            ).scalar_one()
            references[metric.slug] = metric_id

        return references

    def _persist_single_observation(
        self,
        conn: Connection,
        *,
        observation: NormalizedFxObservation,
        references: dict[str, UUID],
        scraper_run_id: UUID | None,
    ) -> PersistObservationResult:
        location_key = observation.location_path or TANZANIA_LOCATION_PATH
        location_id = references.get(location_key)
        if location_id is None:
            location_id = references[TANZANIA_LOCATION_PATH]

        existing = conn.execute(
            text(
                """
                SELECT
                    dp.id,
                    dp.recorded_at,
                    dp.version_no,
                    dp.value_numeric,
                    dp.unit_override,
                    dp.extra_data,
                    dp.ingestion_metadata,
                    erd.instrument_code,
                    erd.instrument_name,
                    erd.instrument_type,
                    erd.quote_code,
                    erd.rate_kind,
                    erd.market_scope,
                    erd.channel,
                    erd.cash_note_band,
                    erd.source_effective_date,
                    erd.source_last_updated_at,
                    erd.inverse_rate
                FROM data_points dp
                JOIN exchange_rate_details erd
                  ON erd.data_point_id = dp.id
                 AND erd.data_point_recorded_at = dp.recorded_at
                WHERE dp.metric_id = :metric_id
                  AND dp.source_id = :source_id
                  AND COALESCE(dp.location_id, :location_id) = :location_id
                  AND dp.recorded_at = :recorded_at
                  AND dp.external_reference = :external_reference
                  AND dp.is_current = true
                LIMIT 1
                """
            ),
            {
                "metric_id": references[observation.metric_slug],
                "source_id": references[observation.source_slug],
                "location_id": location_id,
                "recorded_at": observation.recorded_at,
                "external_reference": observation.external_reference,
            },
        ).mappings().first()

        current_fingerprint = payload_fingerprint(
            value=observation.value,
            unit_override=observation.unit_override,
            detail=observation.detail,
            extra_data=observation.extra_data,
            ingestion_metadata=observation.ingestion_metadata,
        )
        if existing is not None:
            existing_fingerprint = payload_fingerprint(
                value=existing["value_numeric"],
                unit_override=existing["unit_override"] or "TZS",
                detail=observation.detail.__class__(
                    instrument_code=existing["instrument_code"],
                    instrument_name=existing["instrument_name"],
                    instrument_type=existing["instrument_type"],
                    quote_code=existing["quote_code"],
                    rate_kind=existing["rate_kind"],
                    market_scope=existing["market_scope"],
                    channel=existing["channel"],
                    cash_note_band=existing["cash_note_band"],
                    source_effective_date=existing["source_effective_date"],
                    source_last_updated_at=existing["source_last_updated_at"],
                    inverse_rate=existing["inverse_rate"],
                ),
                extra_data=existing["extra_data"] or {},
                ingestion_metadata=existing["ingestion_metadata"] or {},
            )
            if existing_fingerprint == current_fingerprint:
                return PersistObservationResult(skipped=1)

            conn.execute(
                text(
                    """
                    UPDATE data_points
                    SET is_current = false
                    WHERE id = :id AND recorded_at = :recorded_at
                    """
                ),
                {
                    "id": existing["id"],
                    "recorded_at": existing["recorded_at"],
                },
            )
            version_no = int(existing["version_no"]) + 1
            supersedes_id = existing["id"]
            supersedes_recorded_at = existing["recorded_at"]
            updated = 1
        else:
            version_no = 1
            supersedes_id = None
            supersedes_recorded_at = None
            updated = 0

        data_point_id = uuid.uuid4()
        conn.execute(
            text(
                """
                INSERT INTO data_points (
                    id, metric_id, source_id, location_id, scraper_run_id,
                    supersedes_id, supersedes_recorded_at, external_reference,
                    unit_override, value_type, value_numeric, extra_data,
                    ingestion_metadata, recorded_at, version_no, is_current,
                    is_valid, confidence_score, created_at
                )
                VALUES (
                    :id, :metric_id, :source_id, :location_id, :scraper_run_id,
                    :supersedes_id, :supersedes_recorded_at, :external_reference,
                    :unit_override, 'numeric', :value_numeric,
                    CAST(:extra_data AS jsonb),
                    CAST(:ingestion_metadata AS jsonb), :recorded_at, :version_no, true,
                    true, 1.0000, now()
                )
                """
            ),
            {
                "id": data_point_id,
                "metric_id": references[observation.metric_slug],
                "source_id": references[observation.source_slug],
                "location_id": location_id,
                "scraper_run_id": scraper_run_id,
                "supersedes_id": supersedes_id,
                "supersedes_recorded_at": supersedes_recorded_at,
                "external_reference": observation.external_reference,
                "unit_override": observation.unit_override,
                "value_numeric": observation.value,
                "extra_data": json.dumps(observation.extra_data),
                "ingestion_metadata": json.dumps(observation.ingestion_metadata),
                "recorded_at": observation.recorded_at,
                "version_no": version_no,
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO exchange_rate_details (
                    id, data_point_id, data_point_recorded_at, instrument_code,
                    instrument_name, instrument_type, quote_code, rate_kind,
                    market_scope, channel, cash_note_band, source_effective_date,
                    source_last_updated_at, inverse_rate, created_at, updated_at
                )
                VALUES (
                    :id, :data_point_id, :data_point_recorded_at, :instrument_code,
                    :instrument_name, :instrument_type, :quote_code, :rate_kind,
                    :market_scope, :channel, :cash_note_band, :source_effective_date,
                    :source_last_updated_at, :inverse_rate, now(), now()
                )
                """
            ),
            {
                "id": uuid.uuid4(),
                "data_point_id": data_point_id,
                "data_point_recorded_at": observation.recorded_at,
                "instrument_code": observation.detail.instrument_code,
                "instrument_name": observation.detail.instrument_name,
                "instrument_type": observation.detail.instrument_type,
                "quote_code": observation.detail.quote_code,
                "rate_kind": observation.detail.rate_kind,
                "market_scope": observation.detail.market_scope,
                "channel": observation.detail.channel,
                "cash_note_band": observation.detail.cash_note_band,
                "source_effective_date": observation.detail.source_effective_date,
                "source_last_updated_at": observation.detail.source_last_updated_at,
                "inverse_rate": observation.detail.inverse_rate,
            },
        )
        return PersistObservationResult(inserted=1, updated=updated)
