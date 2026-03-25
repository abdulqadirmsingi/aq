"""Write parsed EWURA rows into Postgres (sync; used from Celery / CLI)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import create_engine, text

from src.core.db_url import sync_database_url
from src.domains.energy.ewura.models import EwuraDocumentPayload


def persist_ewura_payload(database_url: str, payload: EwuraDocumentPayload) -> int:
    """
    Insert cap-price rows; idempotent on (sha256, location, fuel, recorded_at).

    Does not import the FastAPI app (see ``rules.md``).
    """
    if not payload.data:
        return 0
    pub: date | None = None
    if payload.published_date:
        pub = date.fromisoformat(payload.published_date)

    engine = create_engine(sync_database_url(database_url), pool_pre_ping=True)
    sql = text(
        """
        INSERT INTO ewura_fuel_observations (
            document_url, content_sha256, published_date,
            location, fuel_type, price, unit, recorded_at
        ) VALUES (
            :document_url, :sha, :published_date,
            :location, :fuel_type, :price, :unit, :recorded_at
        )
        ON CONFLICT (content_sha256, location, fuel_type, recorded_at) DO NOTHING
        """,
    )
    inserted = 0
    try:
        with engine.begin() as conn:
            for rec in payload.data:
                res = conn.execute(
                    sql,
                    {
                        "document_url": payload.document_url,
                        "sha": payload.content_sha256,
                        "published_date": pub,
                        "location": rec.location,
                        "fuel_type": rec.fuel_type,
                        "price": rec.price,
                        "unit": rec.unit,
                        "recorded_at": rec.recorded_at,
                    },
                )
                if res.rowcount:
                    inserted += res.rowcount
    finally:
        engine.dispose()
    return inserted
