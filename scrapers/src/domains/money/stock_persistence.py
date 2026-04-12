"""Persistence layer for normalized DSE stock-price scraper outputs."""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from src.core.db_url import sync_database_url
from src.domains.money.stock_models import (
    NormalizedStockObservation,
    PersistStockResult,
    StockPriceDetailPayload,
)

_SOURCE_SLUG = "itrust_dse"
_METRIC_SLUG = "dse_close_price"
_MONEY_CATEGORY_SLUG = "money"
_LOCATION_PATH = "TZ"


def _stock_fingerprint(
    *,
    close_price: Decimal,
    detail: StockPriceDetailPayload,
    extra_data: dict[str, object],
    ingestion_metadata: dict[str, object],
) -> tuple[object, ...]:
    return (
        close_price,
        detail.symbol,
        detail.exchange_code,
        detail.trade_date,
        detail.open_price,
        detail.high_price,
        detail.low_price,
        detail.change_pct,
        detail.turnover_tzs,
        tuple(sorted(extra_data.items())),
        tuple(sorted(ingestion_metadata.items())),
    )


class StockPersistenceStore:
    """Persist normalized DSE stock observations into the shared platform tables."""

    def __init__(self, database_url: str) -> None:
        self._engine: Engine = create_engine(
            sync_database_url(database_url),
            pool_pre_ping=True,
        )

    def close(self) -> None:
        self._engine.dispose()

    def __enter__(self) -> StockPersistenceStore:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

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
                    "category_id": references[_MONEY_CATEGORY_SLUG],
                    "source_id": references[_SOURCE_SLUG],
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
        observations: Iterable[NormalizedStockObservation],
        *,
        scraper_run_id: UUID | None = None,
    ) -> PersistStockResult:
        result = PersistStockResult()
        observation_list = list(observations)
        if not observation_list:
            return result

        with self._engine.begin() as conn:
            references = self._ensure_reference_ids(conn)
            for obs in observation_list:
                result += self._persist_single(
                    conn,
                    observation=obs,
                    references=references,
                    scraper_run_id=scraper_run_id,
                )
        return result

    def _ensure_reference_ids(self, conn: Connection) -> dict[str, UUID]:
        references: dict[str, UUID] = {}

        category_id = conn.execute(
            text(
                """
                SELECT id FROM data_categories WHERE slug = :slug
                """
            ),
            {"slug": _MONEY_CATEGORY_SLUG},
        ).scalar_one()
        references[_MONEY_CATEGORY_SLUG] = category_id

        location_id = conn.execute(
            text("SELECT id FROM locations WHERE path = :path"),
            {"path": _LOCATION_PATH},
        ).scalar_one()
        references[_LOCATION_PATH] = location_id

        source_id = conn.execute(
            text("SELECT id FROM sources WHERE slug = :slug"),
            {"slug": _SOURCE_SLUG},
        ).scalar_one()
        references[_SOURCE_SLUG] = source_id

        metric_id = conn.execute(
            text("SELECT id FROM metrics WHERE slug = :slug"),
            {"slug": _METRIC_SLUG},
        ).scalar_one()
        references[_METRIC_SLUG] = metric_id

        return references

    def _persist_single(
        self,
        conn: Connection,
        *,
        observation: NormalizedStockObservation,
        references: dict[str, UUID],
        scraper_run_id: UUID | None,
    ) -> PersistStockResult:
        location_id = references[_LOCATION_PATH]
        metric_id = references[_METRIC_SLUG]
        source_id = references[_SOURCE_SLUG]

        existing = conn.execute(
            text(
                """
                SELECT
                    dp.id,
                    dp.recorded_at,
                    dp.version_no,
                    dp.value_numeric,
                    dp.extra_data,
                    dp.ingestion_metadata,
                    spd.symbol,
                    spd.exchange_code,
                    spd.trade_date,
                    spd.open_price,
                    spd.high_price,
                    spd.low_price,
                    spd.change_pct,
                    spd.turnover_tzs
                FROM data_points dp
                JOIN stock_price_details spd
                  ON spd.data_point_id = dp.id
                 AND spd.data_point_recorded_at = dp.recorded_at
                WHERE dp.metric_id = :metric_id
                  AND dp.source_id = :source_id
                  AND dp.location_id = :location_id
                  AND dp.recorded_at = :recorded_at
                  AND dp.external_reference = :external_reference
                  AND dp.is_current = true
                LIMIT 1
                """
            ),
            {
                "metric_id": metric_id,
                "source_id": source_id,
                "location_id": location_id,
                "recorded_at": observation.recorded_at,
                "external_reference": observation.external_reference,
            },
        ).mappings().first()

        current_fp = _stock_fingerprint(
            close_price=observation.value,
            detail=observation.detail,
            extra_data=observation.extra_data,
            ingestion_metadata=observation.ingestion_metadata,
        )

        if existing is not None:
            existing_fp = _stock_fingerprint(
                close_price=existing["value_numeric"],
                detail=StockPriceDetailPayload(
                    symbol=existing["symbol"],
                    trade_date=existing["trade_date"],
                    exchange_code=existing["exchange_code"],
                    open_price=existing["open_price"],
                    high_price=existing["high_price"],
                    low_price=existing["low_price"],
                    change_pct=existing["change_pct"],
                    turnover_tzs=existing["turnover_tzs"],
                ),
                extra_data=existing["extra_data"] or {},
                ingestion_metadata=existing["ingestion_metadata"] or {},
            )
            if existing_fp == current_fp:
                return PersistStockResult(skipped=1)

            conn.execute(
                text(
                    """
                    UPDATE data_points
                    SET is_current = false
                    WHERE id = :id AND recorded_at = :recorded_at
                    """
                ),
                {"id": existing["id"], "recorded_at": existing["recorded_at"]},
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
                    unit_override, value_type, value_numeric,
                    extra_data, ingestion_metadata,
                    recorded_at, version_no, is_current, is_valid,
                    confidence_score, created_at
                )
                VALUES (
                    :id, :metric_id, :source_id, :location_id, :scraper_run_id,
                    :supersedes_id, :supersedes_recorded_at, :external_reference,
                    :unit_override, 'numeric', :value_numeric,
                    CAST(:extra_data AS jsonb), CAST(:ingestion_metadata AS jsonb),
                    :recorded_at, :version_no, true, true, 1.0000, now()
                )
                """
            ),
            {
                "id": data_point_id,
                "metric_id": metric_id,
                "source_id": source_id,
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

        detail = observation.detail
        conn.execute(
            text(
                """
                INSERT INTO stock_price_details (
                    id, data_point_id, data_point_recorded_at,
                    symbol, exchange_code,
                    open_price, high_price, low_price,
                    change_pct, turnover_tzs, trade_date,
                    created_at, updated_at
                )
                VALUES (
                    :id, :data_point_id, :data_point_recorded_at,
                    :symbol, :exchange_code,
                    :open_price, :high_price, :low_price,
                    :change_pct, :turnover_tzs, :trade_date,
                    now(), now()
                )
                """
            ),
            {
                "id": uuid.uuid4(),
                "data_point_id": data_point_id,
                "data_point_recorded_at": observation.recorded_at,
                "symbol": detail.symbol,
                "exchange_code": detail.exchange_code,
                "open_price": detail.open_price,
                "high_price": detail.high_price,
                "low_price": detail.low_price,
                "change_pct": detail.change_pct,
                "turnover_tzs": detail.turnover_tzs,
                "trade_date": detail.trade_date,
            },
        )

        return PersistStockResult(inserted=1, updated=updated)
