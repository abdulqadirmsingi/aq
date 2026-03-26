"""Persist per-URL / per-hash ingestion state (PostgreSQL, sync engine)."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.core.db_url import sync_database_url


class DocumentFingerprintStore:
    """
    One row per ``(source_slug, document_url)``; supports hash-based short-circuit.

    Rows with ``parse_ok=false`` are retried on the next run. Successful URLs are
    skipped when ``ewura_skip_successful_urls`` is enabled.
    """

    def __init__(self, database_url: str, source_slug: str) -> None:
        self._source_slug = source_slug
        self._engine: Engine = create_engine(
            sync_database_url(database_url),
            pool_pre_ping=True,
        )

    def close(self) -> None:
        self._engine.dispose()

    def url_parse_succeeded(self, document_url: str) -> bool:
        with self._engine.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT 1 FROM document_ingestion_fingerprints "
                    "WHERE source_slug = :slug AND document_url = :url "
                    "AND parse_ok = true LIMIT 1",
                ),
                {"slug": self._source_slug, "url": document_url},
            ).first()
            return row is not None

    def has_successful_hash(self, content_sha256: str) -> bool:
        with self._engine.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT 1 FROM document_ingestion_fingerprints "
                    "WHERE source_slug = :slug AND content_sha256 = :sha "
                    "AND parse_ok = true LIMIT 1",
                ),
                {"slug": self._source_slug, "sha": content_sha256},
            ).first()
            return row is not None

    def upsert(
        self,
        *,
        document_url: str,
        content_sha256: str,
        parse_ok: bool,
        records_extracted: int,
    ) -> None:
        stmt = text(
            """
            INSERT INTO document_ingestion_fingerprints (
                source_slug, document_url, content_sha256,
                parse_ok, records_extracted, created_at, updated_at
            )
            VALUES (
                :slug, :url, :sha, :ok, :n, now(), now()
            )
            ON CONFLICT (source_slug, document_url)
            DO UPDATE SET
                content_sha256 = EXCLUDED.content_sha256,
                parse_ok = EXCLUDED.parse_ok,
                records_extracted = EXCLUDED.records_extracted,
                updated_at = now()
            """,
        )
        with self._engine.begin() as conn:
            conn.execute(
                stmt,
                {
                    "slug": self._source_slug,
                    "url": document_url,
                    "sha": content_sha256,
                    "ok": parse_ok,
                    "n": records_extracted,
                },
            )
