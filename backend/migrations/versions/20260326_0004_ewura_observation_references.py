"""Add reference foreign keys to EWURA observations.

Revision ID: 20260326_0004
Revises: 20260326_0003
Create Date: 2026-03-26 14:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260326_0004"
down_revision: str | None = "20260326_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ewura_fuel_observations",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "ewura_fuel_observations",
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "ewura_fuel_observations",
        sa.Column("scraper_run_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_ewura_fuel_observations_source_id_sources"),
        "ewura_fuel_observations",
        "sources",
        ["source_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_ewura_fuel_observations_location_id_locations"),
        "ewura_fuel_observations",
        "locations",
        ["location_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_ewura_fuel_observations_scraper_run_id_scraper_runs"),
        "ewura_fuel_observations",
        "scraper_runs",
        ["scraper_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_ewura_fuel_observations_source_id"),
        "ewura_fuel_observations",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ewura_fuel_observations_location_id"),
        "ewura_fuel_observations",
        ["location_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ewura_fuel_observations_scraper_run_id"),
        "ewura_fuel_observations",
        ["scraper_run_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_ewura_fuel_observations_scraper_run_id"),
        table_name="ewura_fuel_observations",
    )
    op.drop_index(
        op.f("ix_ewura_fuel_observations_location_id"),
        table_name="ewura_fuel_observations",
    )
    op.drop_index(
        op.f("ix_ewura_fuel_observations_source_id"),
        table_name="ewura_fuel_observations",
    )
    op.drop_constraint(
        op.f("fk_ewura_fuel_observations_scraper_run_id_scraper_runs"),
        "ewura_fuel_observations",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_ewura_fuel_observations_location_id_locations"),
        "ewura_fuel_observations",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_ewura_fuel_observations_source_id_sources"),
        "ewura_fuel_observations",
        type_="foreignkey",
    )
    op.drop_column("ewura_fuel_observations", "scraper_run_id")
    op.drop_column("ewura_fuel_observations", "location_id")
    op.drop_column("ewura_fuel_observations", "source_id")
