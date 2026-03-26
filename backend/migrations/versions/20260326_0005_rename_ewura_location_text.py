"""Rename EWURA raw location text column.

Revision ID: 20260326_0005
Revises: 20260326_0004
Create Date: 2026-03-26 16:30:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260326_0005"
down_revision: str | None = "20260326_0004"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "ewura_fuel_observations",
        "location",
        new_column_name="raw_location_text",
    )


def downgrade() -> None:
    op.alter_column(
        "ewura_fuel_observations",
        "raw_location_text",
        new_column_name="location",
    )
