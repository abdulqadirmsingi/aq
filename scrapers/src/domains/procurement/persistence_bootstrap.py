"""Reference-data bootstrap for the procurement domain (category + source)."""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.domains.procurement.constants import (
    NEST_SOURCE_DESCRIPTION,
    NEST_SOURCE_NAME,
    NEST_SOURCE_SLUG,
    NEST_SOURCE_URL,
    PROCUREMENT_CATEGORY_DESCRIPTION,
    PROCUREMENT_CATEGORY_NAME,
    PROCUREMENT_CATEGORY_SLUG,
)


def ensure_reference_ids(conn: Connection) -> dict[str, UUID]:
    """Upsert procurement category and NeST source; return their IDs by slug."""
    refs: dict[str, UUID] = {}

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
            "slug": PROCUREMENT_CATEGORY_SLUG,
            "name": PROCUREMENT_CATEGORY_NAME,
            "description": PROCUREMENT_CATEGORY_DESCRIPTION,
        },
    ).scalar_one()
    refs[PROCUREMENT_CATEGORY_SLUG] = category_id

    source_id = conn.execute(
        text(
            """
            INSERT INTO sources (
                id, slug, name, source_type, description, url,
                reliability_score, is_active, metadata, created_at, updated_at
            )
            VALUES (
                :id, :slug, :name, 'government', :description, :url,
                0.900, true, '{}'::jsonb, now(), now()
            )
            ON CONFLICT (slug) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                url = EXCLUDED.url,
                updated_at = now()
            RETURNING id
            """
        ),
        {
            "id": uuid.uuid4(),
            "slug": NEST_SOURCE_SLUG,
            "name": NEST_SOURCE_NAME,
            "description": NEST_SOURCE_DESCRIPTION,
            "url": NEST_SOURCE_URL,
        },
    ).scalar_one()
    refs[NEST_SOURCE_SLUG] = source_id

    return refs
