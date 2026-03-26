"""Expand exchange-rate schema and seed phase-1 catalog.

Revision ID: 20260326_0007
Revises: 20260326_0006
Create Date: 2026-03-26 20:15:00
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260326_0007"
down_revision: str | None = "20260326_0006"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

MONEY_CATEGORY_ID = "f7111111-1111-4111-8111-111111111111"
BOT_SOURCE_ID = "f7222222-2222-4222-8222-222222222222"
CRDB_SOURCE_ID = "f7333333-3333-4333-8333-333333333333"
NMB_SOURCE_ID = "f7444444-4444-4444-8444-444444444444"
TZ_LOCATION_ID = "f7555555-5555-4555-8555-555555555555"
FX_BUY_METRIC_ID = "f7666666-6666-4666-8666-666666666666"
FX_SELL_METRIC_ID = "f7777777-7777-4777-8777-777777777777"
FX_MEAN_METRIC_ID = "f7888888-8888-4888-8888-888888888888"


def _seed_reference_catalog() -> None:
    bind = op.get_bind()
    validation_rules = json.dumps({"minimum": 0})
    dimensions_schema = json.dumps(
        {
            "instrument_code": "string",
            "quote_code": "string",
            "market_scope": "string",
            "channel": "string|null",
            "cash_note_band": "string|null",
            "source_effective_date": "date|null",
            "source_last_updated_at": "datetime|null",
        }
    )

    bind.execute(
        sa.text(
            """
            INSERT INTO data_categories (
                id, slug, name, description, config, created_at, updated_at
            )
            VALUES (
                :id, 'money', 'Money',
                'Exchange rates, inflation, and financial market observations.',
                '{}'::jsonb, now(), now()
            )
            ON CONFLICT (slug) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                updated_at = now()
            """
        ),
        {"id": MONEY_CATEGORY_ID},
    )

    for source_id, slug, name, source_type, description, url, reliability in (
        (
            BOT_SOURCE_ID,
            "bot_exchange_rates",
            "Bank of Tanzania Exchange Rates",
            "government",
            "Official Bank of Tanzania exchange-rate reference tables.",
            "https://www.bot.go.tz/exchangerate/excrates",
            "0.980",
        ),
        (
            CRDB_SOURCE_ID,
            "crdb_forex",
            "CRDB Forex Rates",
            "private",
            "CRDB Bank foreign-exchange buy and sell rates.",
            "https://crdbbank.co.tz/en/forex",
            "0.900",
        ),
        (
            NMB_SOURCE_ID,
            "nmb_daily_exchange_rates",
            "NMB Daily Exchange Rates",
            "private",
            "NMB Bank daily non-cash and cash foreign-exchange rates.",
            "https://www.nmbbank.co.tz/treasury/foreign-exchange/nmb-daily-exchange-rates",
            "0.900",
        ),
    ):
        bind.execute(
            sa.text(
                """
                INSERT INTO sources (
                    id, slug, name, source_type, description, url, reliability_score,
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
                """
            ),
            {
                "id": source_id,
                "slug": slug,
                "name": name,
                "source_type": source_type,
                "description": description,
                "url": url,
                "reliability_score": reliability,
            },
        )

    bind.execute(
        sa.text(
            """
            INSERT INTO locations (
                id, name, code, level, parent_id, country_code, path,
                is_active, created_at, updated_at
            )
            VALUES (
                :id, 'Tanzania', 'TZ', 'country', NULL, 'TZA', 'TZ',
                true, now(), now()
            )
            ON CONFLICT (path) DO UPDATE SET
                name = EXCLUDED.name,
                code = EXCLUDED.code,
                country_code = EXCLUDED.country_code,
                updated_at = now()
            """
        ),
        {"id": TZ_LOCATION_ID},
    )

    for metric_id, slug, name, description in (
        (
            FX_BUY_METRIC_ID,
            "fx_buy_rate",
            "FX Buy Rate",
            "Observed source buying rate quoted against TZS.",
        ),
        (
            FX_SELL_METRIC_ID,
            "fx_sell_rate",
            "FX Sell Rate",
            "Observed source selling rate quoted against TZS.",
        ),
        (
            FX_MEAN_METRIC_ID,
            "fx_mean_rate",
            "FX Mean Rate",
            "Observed source midpoint or mean rate quoted against TZS.",
        ),
    ):
        bind.execute(
            sa.text(
                """
                INSERT INTO metrics (
                    id, slug, name, unit, description, category_id, canonical_source_id,
                    value_type, default_frequency, is_location_required,
                    validation_rules, dimensions_schema, created_at, updated_at
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
                    canonical_source_id = EXCLUDED.canonical_source_id,
                    value_type = EXCLUDED.value_type,
                    default_frequency = EXCLUDED.default_frequency,
                    is_location_required = EXCLUDED.is_location_required,
                    validation_rules = EXCLUDED.validation_rules,
                    dimensions_schema = EXCLUDED.dimensions_schema,
                    updated_at = now()
                """
            ),
            {
                "id": metric_id,
                "slug": slug,
                "name": name,
                "description": description,
                "category_id": MONEY_CATEGORY_ID,
                "validation_rules": validation_rules,
                "dimensions_schema": dimensions_schema,
            },
        )


def upgrade() -> None:
    op.drop_index("ix_exchange_rate_details_market", table_name="exchange_rate_details")
    op.drop_index("ix_exchange_rate_details_pair", table_name="exchange_rate_details")

    op.alter_column(
        "exchange_rate_details",
        "base_currency",
        new_column_name="instrument_code",
        existing_type=sa.String(length=3),
    )
    op.alter_column(
        "exchange_rate_details",
        "quote_currency",
        new_column_name="quote_code",
        existing_type=sa.String(length=3),
    )
    op.alter_column(
        "exchange_rate_details",
        "rate_type",
        new_column_name="rate_kind",
        existing_type=sa.String(length=32),
    )
    op.alter_column(
        "exchange_rate_details",
        "market",
        new_column_name="market_scope",
        existing_type=sa.String(length=32),
    )

    op.alter_column(
        "exchange_rate_details", "instrument_code", type_=sa.String(length=16)
    )
    op.alter_column("exchange_rate_details", "quote_code", type_=sa.String(length=16))
    op.alter_column("exchange_rate_details", "rate_kind", type_=sa.String(length=24))
    op.alter_column("exchange_rate_details", "market_scope", type_=sa.String(length=32))

    op.add_column(
        "exchange_rate_details",
        sa.Column("instrument_name", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "exchange_rate_details",
        sa.Column(
            "instrument_type",
            sa.String(length=24),
            nullable=False,
            server_default="currency",
        ),
    )
    op.add_column(
        "exchange_rate_details",
        sa.Column(
            "channel",
            sa.String(length=32),
            nullable=True,
        ),
    )
    op.add_column(
        "exchange_rate_details",
        sa.Column(
            "cash_note_band",
            sa.String(length=32),
            nullable=True,
        ),
    )
    op.add_column(
        "exchange_rate_details",
        sa.Column("source_effective_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "exchange_rate_details",
        sa.Column("source_last_updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.execute(
        """
        UPDATE exchange_rate_details
        SET quote_code = COALESCE(NULLIF(quote_code, ''), 'TZS'),
            rate_kind = COALESCE(NULLIF(rate_kind, ''), 'unknown'),
            market_scope = COALESCE(NULLIF(market_scope, ''), 'unknown')
        """
    )

    op.alter_column(
        "exchange_rate_details",
        "quote_code",
        existing_type=sa.String(length=16),
        nullable=False,
        server_default="TZS",
    )
    op.alter_column(
        "exchange_rate_details",
        "rate_kind",
        existing_type=sa.String(length=24),
        nullable=False,
    )
    op.alter_column(
        "exchange_rate_details",
        "market_scope",
        existing_type=sa.String(length=32),
        nullable=False,
    )

    op.create_index(
        "ix_exchange_rate_details_lookup",
        "exchange_rate_details",
        ["instrument_code", "quote_code", "rate_kind", "data_point_recorded_at"],
        unique=False,
    )
    op.create_index(
        "ix_exchange_rate_details_market_channel",
        "exchange_rate_details",
        ["market_scope", "channel"],
        unique=False,
    )
    op.create_index(
        "ix_exchange_rate_details_source_effective_date",
        "exchange_rate_details",
        ["source_effective_date"],
        unique=False,
    )
    op.create_index(
        "ix_exchange_rate_details_source_last_updated_at",
        "exchange_rate_details",
        ["source_last_updated_at"],
        unique=False,
    )

    _seed_reference_catalog()


def downgrade() -> None:
    bind = op.get_bind()

    bind.execute(
        sa.text(
            """
            DELETE FROM metrics
            WHERE slug IN ('fx_buy_rate', 'fx_sell_rate', 'fx_mean_rate')
            """
        )
    )
    bind.execute(
        sa.text(
            """
            DELETE FROM sources
            WHERE slug IN (
                'bot_exchange_rates',
                'crdb_forex',
                'nmb_daily_exchange_rates'
            )
            """
        )
    )
    bind.execute(
        sa.text(
            """
            DELETE FROM data_categories
            WHERE slug = 'money'
              AND NOT EXISTS (
                  SELECT 1 FROM metrics
                  WHERE metrics.category_id = data_categories.id
              )
              AND NOT EXISTS (
                  SELECT 1 FROM scraper_runs
                  WHERE scraper_runs.category_id = data_categories.id
              )
            """
        )
    )
    bind.execute(
        sa.text(
            """
            DELETE FROM locations
            WHERE path = 'TZ'
              AND NOT EXISTS (
                  SELECT 1 FROM data_points
                  WHERE data_points.location_id = locations.id
              )
              AND NOT EXISTS (
                  SELECT 1 FROM locations child
                  WHERE child.parent_id = locations.id
              )
            """
        )
    )

    op.drop_index(
        "ix_exchange_rate_details_source_last_updated_at",
        table_name="exchange_rate_details",
    )
    op.drop_index(
        "ix_exchange_rate_details_source_effective_date",
        table_name="exchange_rate_details",
    )
    op.drop_index(
        "ix_exchange_rate_details_market_channel",
        table_name="exchange_rate_details",
    )
    op.drop_index("ix_exchange_rate_details_lookup", table_name="exchange_rate_details")

    op.drop_column("exchange_rate_details", "source_last_updated_at")
    op.drop_column("exchange_rate_details", "source_effective_date")
    op.drop_column("exchange_rate_details", "cash_note_band")
    op.drop_column("exchange_rate_details", "channel")
    op.drop_column("exchange_rate_details", "instrument_type")
    op.drop_column("exchange_rate_details", "instrument_name")

    op.alter_column(
        "exchange_rate_details",
        "market_scope",
        existing_type=sa.String(length=32),
        type_=sa.String(length=32),
        nullable=True,
    )
    op.alter_column(
        "exchange_rate_details",
        "rate_kind",
        existing_type=sa.String(length=24),
        type_=sa.String(length=32),
        nullable=True,
    )
    op.alter_column(
        "exchange_rate_details",
        "quote_code",
        existing_type=sa.String(length=16),
        type_=sa.String(length=3),
        server_default=None,
    )
    op.alter_column(
        "exchange_rate_details",
        "instrument_code",
        existing_type=sa.String(length=16),
        type_=sa.String(length=3),
    )

    op.alter_column(
        "exchange_rate_details",
        "market_scope",
        new_column_name="market",
        existing_type=sa.String(length=32),
    )
    op.alter_column(
        "exchange_rate_details",
        "rate_kind",
        new_column_name="rate_type",
        existing_type=sa.String(length=32),
    )
    op.alter_column(
        "exchange_rate_details",
        "quote_code",
        new_column_name="quote_currency",
        existing_type=sa.String(length=3),
    )
    op.alter_column(
        "exchange_rate_details",
        "instrument_code",
        new_column_name="base_currency",
        existing_type=sa.String(length=3),
    )

    op.create_index(
        "ix_exchange_rate_details_pair",
        "exchange_rate_details",
        ["base_currency", "quote_currency"],
        unique=False,
    )
    op.create_index(
        "ix_exchange_rate_details_market",
        "exchange_rate_details",
        ["market"],
        unique=False,
    )
