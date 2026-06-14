"""Add procurement_tenders table.

Revision ID: 20260613_0009
Revises: 20260412_0008
Create Date: 2026-06-13 00:00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260613_0009"
down_revision: str | None = "20260412_0008"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "procurement_tenders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ocid", sa.String(255), nullable=False),
        sa.Column("tender_reference", sa.String(255), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("procuring_entity_name", sa.String(500), nullable=True),
        sa.Column("procuring_entity_id", sa.String(255), nullable=True),
        sa.Column("procurement_method", sa.String(64), nullable=True),
        sa.Column("procurement_method_details", sa.String(255), nullable=True),
        sa.Column("tender_status", sa.String(64), nullable=True),
        sa.Column("tender_value_amount", sa.Numeric(20, 2), nullable=True),
        sa.Column("tender_value_currency", sa.String(8), nullable=True),
        sa.Column(
            "tender_period_start",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "tender_period_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "has_award",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("award_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("award_value_amount", sa.Numeric(20, 2), nullable=True),
        sa.Column("award_value_currency", sa.String(8), nullable=True),
        sa.Column("contractor_name", sa.String(500), nullable=True),
        sa.Column("contractor_id", sa.String(255), nullable=True),
        sa.Column("financial_year", sa.String(16), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column(
            "raw_ocds",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("raw_ocds_fingerprint", sa.String(32), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_procurement_tenders"),
    )

    op.create_index(
        "ix_procurement_tenders_ocid",
        "procurement_tenders",
        ["ocid"],
        unique=True,
    )
    op.create_index(
        "ix_procurement_tenders_tender_status",
        "procurement_tenders",
        ["tender_status"],
    )
    op.create_index(
        "ix_procurement_tenders_has_award",
        "procurement_tenders",
        ["has_award"],
    )
    op.create_index(
        "ix_procurement_tenders_procurement_method",
        "procurement_tenders",
        ["procurement_method"],
    )
    op.create_index(
        "ix_procurement_tenders_procuring_entity_id",
        "procurement_tenders",
        ["procuring_entity_id"],
    )
    op.create_index(
        "ix_procurement_tenders_tender_period_end",
        "procurement_tenders",
        ["tender_period_end"],
    )
    op.create_index(
        "ix_procurement_tenders_award_date",
        "procurement_tenders",
        ["award_date"],
    )
    op.create_index(
        "ix_procurement_tenders_financial_year",
        "procurement_tenders",
        ["financial_year"],
    )
    op.create_index(
        "ix_procurement_tenders_raw_ocds_gin",
        "procurement_tenders",
        ["raw_ocds"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_procurement_tenders_raw_ocds_gin", table_name="procurement_tenders")
    op.drop_index("ix_procurement_tenders_financial_year", table_name="procurement_tenders")
    op.drop_index("ix_procurement_tenders_award_date", table_name="procurement_tenders")
    op.drop_index("ix_procurement_tenders_tender_period_end", table_name="procurement_tenders")
    op.drop_index("ix_procurement_tenders_procuring_entity_id", table_name="procurement_tenders")
    op.drop_index("ix_procurement_tenders_procurement_method", table_name="procurement_tenders")
    op.drop_index("ix_procurement_tenders_has_award", table_name="procurement_tenders")
    op.drop_index("ix_procurement_tenders_tender_status", table_name="procurement_tenders")
    op.drop_index("ix_procurement_tenders_ocid", table_name="procurement_tenders")
    op.drop_table("procurement_tenders")
