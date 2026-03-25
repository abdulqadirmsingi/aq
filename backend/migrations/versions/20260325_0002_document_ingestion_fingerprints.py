"""Add document_ingestion_fingerprints for scraper deduplication.

Revision ID: 20260325_0002
Revises: 20260324_0001
Create Date: 2026-03-25 12:00:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260325_0002"
down_revision: str | None = "20260324_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "document_ingestion_fingerprints",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("source_slug", sa.String(length=64), nullable=False),
        sa.Column("document_url", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("parse_ok", sa.Boolean(), nullable=False),
        sa.Column(
            "records_extracted",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_ingestion_fingerprints")),
        sa.UniqueConstraint(
            "source_slug",
            "document_url",
            name=op.f("uq_document_ingestion_fingerprints_source_url"),
        ),
    )
    op.create_index(
        op.f("ix_document_ingestion_fingerprints_source_sha_ok"),
        "document_ingestion_fingerprints",
        ["source_slug", "content_sha256", "parse_ok"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_document_ingestion_fingerprints_source_sha_ok"),
        table_name="document_ingestion_fingerprints",
    )
    op.drop_table("document_ingestion_fingerprints")
