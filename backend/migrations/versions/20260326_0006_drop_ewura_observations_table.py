"""Drop EWURA-specific observation table after normalization.

Revision ID: 20260326_0006
Revises: 20260326_0005
Create Date: 2026-03-26 18:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260326_0006"
down_revision: str | None = "20260326_0005"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_table("ewura_fuel_observations")


def downgrade() -> None:
    raise NotImplementedError(
        "Recreating ewura_fuel_observations is intentionally unsupported; rerun older migrations if needed."
    )
