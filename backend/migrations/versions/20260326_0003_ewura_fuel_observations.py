"""EWURA fuel cap-price rows for API reads (Phase 5).

Revision ID: 20260326_0003
Revises: 20260325_0002
Create Date: 2026-03-26 12:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260326_0003"
down_revision: str | None = "20260325_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ewura_fuel_observations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "source_label",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'EWURA'"),
        ),
        sa.Column("document_url", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("published_date", sa.Date(), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=False),
        sa.Column("fuel_type", sa.String(length=32), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column(
            "unit",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'TZS/Litre'"),
        ),
        sa.Column("recorded_at", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ewura_fuel_observations")),
        sa.UniqueConstraint(
            "content_sha256",
            "location",
            "fuel_type",
            "recorded_at",
            name=op.f("uq_ewura_fuel_observations_dedupe"),
        ),
    )
    op.create_index(
        op.f("ix_ewura_fuel_observations_published_date"),
        "ewura_fuel_observations",
        ["published_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ewura_fuel_observations_created_at"),
        "ewura_fuel_observations",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_ewura_fuel_observations_created_at"),
        table_name="ewura_fuel_observations",
    )
    op.drop_index(
        op.f("ix_ewura_fuel_observations_published_date"),
        table_name="ewura_fuel_observations",
    )
    op.drop_table("ewura_fuel_observations")
