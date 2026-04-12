"""Add stock_price_details table and seed iTrust DSE catalog.

Revision ID: 20260412_0008
Revises: 20260326_0007
Create Date: 2026-04-12 00:00:00
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260412_0008"
down_revision: str | None = "20260326_0007"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

# Fixed UUIDs for idempotent seeding
MONEY_CATEGORY_ID = "f7111111-1111-4111-8111-111111111111"
TZ_LOCATION_ID = "f7555555-5555-4555-8555-555555555555"
ITRUST_SOURCE_ID = "f7900000-0000-4000-8000-000000000001"
DSE_CLOSE_METRIC_ID = "f7900000-0000-4000-8000-000000000002"


def _seed_reference_catalog() -> None:
    bind = op.get_bind()

    bind.execute(
        sa.text(
            """
            INSERT INTO sources (
                id, slug, name, source_type, description, url, reliability_score,
                is_active, metadata, created_at, updated_at
            )
            VALUES (
                :id, 'itrust_dse', 'iTrust DSE Market Summary', 'private',
                'Daily DSE stock OHLCV data aggregated and published by iTrust Finance.',
                'https://itrust.co.tz/today-market',
                0.880,
                true, '{}'::jsonb, now(), now()
            )
            ON CONFLICT (slug) DO UPDATE SET
                name = EXCLUDED.name,
                source_type = EXCLUDED.source_type,
                description = EXCLUDED.description,
                url = EXCLUDED.url,
                reliability_score = EXCLUDED.reliability_score,
                updated_at = now()
            """
        ),
        {"id": ITRUST_SOURCE_ID},
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO metrics (
                id, slug, name, unit, description, category_id, canonical_source_id,
                value_type, default_frequency, is_location_required,
                validation_rules, dimensions_schema, created_at, updated_at
            )
            VALUES (
                :id, 'dse_close_price', 'DSE Daily Close Price', 'TZS',
                'Daily closing price of a DSE-listed equity or ETF in TZS.',
                :category_id, :source_id,
                'numeric', 'daily', false,
                CAST(:validation_rules AS jsonb),
                CAST(:dimensions_schema AS jsonb),
                now(), now()
            )
            ON CONFLICT (slug) DO UPDATE SET
                name = EXCLUDED.name,
                unit = EXCLUDED.unit,
                description = EXCLUDED.description,
                category_id = EXCLUDED.category_id,
                canonical_source_id = EXCLUDED.canonical_source_id,
                default_frequency = EXCLUDED.default_frequency,
                validation_rules = EXCLUDED.validation_rules,
                dimensions_schema = EXCLUDED.dimensions_schema,
                updated_at = now()
            """
        ),
        {
            "id": DSE_CLOSE_METRIC_ID,
            "category_id": MONEY_CATEGORY_ID,
            "source_id": ITRUST_SOURCE_ID,
            "validation_rules": json.dumps({"minimum": 0}),
            "dimensions_schema": json.dumps(
                {
                    "symbol": {"type": "string"},
                    "exchange_code": {"type": "string"},
                    "trade_date": {"type": "string", "format": "date"},
                }
            ),
        },
    )


def upgrade() -> None:
    op.create_table(
        "stock_price_details",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_point_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_point_recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column(
            "exchange_code",
            sa.String(length=10),
            nullable=False,
            server_default="DSE",
        ),
        sa.Column("open_price", sa.Numeric(24, 4), nullable=True),
        sa.Column("high_price", sa.Numeric(24, 4), nullable=True),
        sa.Column("low_price", sa.Numeric(24, 4), nullable=True),
        sa.Column("change_pct", sa.Numeric(10, 4), nullable=True),
        sa.Column("turnover_tzs", sa.Numeric(24, 4), nullable=True),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["data_point_id", "data_point_recorded_at"],
            ["data_points.id", "data_points.recorded_at"],
            name=op.f("fk_stock_price_details_data_point_data_points"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_stock_price_details")),
        sa.UniqueConstraint(
            "data_point_id",
            "data_point_recorded_at",
            name=op.f("uq_stock_price_details_data_point"),
        ),
    )
    op.create_index(
        "ix_stock_price_details_symbol",
        "stock_price_details",
        ["symbol"],
        unique=False,
    )
    op.create_index(
        "ix_stock_price_details_trade_date",
        "stock_price_details",
        ["trade_date"],
        unique=False,
    )
    op.create_index(
        "ix_stock_price_details_symbol_trade_date",
        "stock_price_details",
        ["symbol", "trade_date"],
        unique=False,
    )

    _seed_reference_catalog()


def downgrade() -> None:
    bind = op.get_bind()

    bind.execute(
        sa.text("DELETE FROM metrics WHERE slug = 'dse_close_price'")
    )
    bind.execute(
        sa.text("DELETE FROM sources WHERE slug = 'itrust_dse'")
    )

    op.drop_index("ix_stock_price_details_symbol_trade_date", table_name="stock_price_details")
    op.drop_index("ix_stock_price_details_trade_date", table_name="stock_price_details")
    op.drop_index("ix_stock_price_details_symbol", table_name="stock_price_details")
    op.drop_table("stock_price_details")
