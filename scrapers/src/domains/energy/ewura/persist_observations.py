"""Backward-compatible wrapper around EWURA persistence helpers."""

from __future__ import annotations

from src.domains.energy.ewura.models import EwuraDocumentPayload
from src.domains.energy.ewura.persistence import EwuraPersistenceStore


def persist_ewura_payload(database_url: str, payload: EwuraDocumentPayload) -> int:
    store = EwuraPersistenceStore(database_url)
    try:
        _category_id, source_id, _country_id = store.ensure_reference_ids()
        return store.persist_payload(payload, scraper_run_id=None, source_id=source_id)
    finally:
        store.close()
