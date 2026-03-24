"""Create AQ data platform schema.

Revision ID: 20260324_0001
Revises:
Create Date: 2026-03-24 00:01:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260324_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


source_type_enum = sa.Enum(
    "government",
    "private",
    "api",
    "scraped",
    "partner",
    "other",
    name="source_type_enum",
)
metric_value_type_enum = sa.Enum(
    "numeric",
    "text",
    "boolean",
    "json",
    name="metric_value_type_enum",
)
metric_frequency_enum = sa.Enum(
    "real_time",
    "hourly",
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "yearly",
    "ad_hoc",
    name="metric_frequency_enum",
)
location_level_enum = sa.Enum(
    "country",
    "region",
    "city",
    "district",
    "ward",
    "other",
    name="location_level_enum",
)
scraper_run_status_enum = sa.Enum(
    "pending",
    "running",
    "succeeded",
    "failed",
    "partial",
    "cancelled",
    name="scraper_run_status_enum",
)


def upgrade() -> None:
    bind = op.get_bind()
    source_type_enum.create(bind, checkfirst=True)
    metric_value_type_enum.create(bind, checkfirst=True)
    metric_frequency_enum.create(bind, checkfirst=True)
    location_level_enum.create(bind, checkfirst=True)
    scraper_run_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "data_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_data_categories")),
        sa.UniqueConstraint("name", name=op.f("uq_data_categories_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_data_categories_slug")),
    )

    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("source_type", source_type_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column(
            "reliability_score",
            sa.Numeric(4, 3),
            nullable=False,
            server_default=sa.text("0.500"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
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
        sa.CheckConstraint(
            "reliability_score >= 0 AND reliability_score <= 1",
            name=op.f("ck_sources_reliability_score_range"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sources")),
        sa.UniqueConstraint("name", name=op.f("uq_sources_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_sources_slug")),
    )

    op.create_table(
        "metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("canonical_source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "value_type",
            metric_value_type_enum,
            nullable=False,
            server_default=sa.text("'numeric'"),
        ),
        sa.Column("default_frequency", metric_frequency_enum, nullable=True),
        sa.Column(
            "is_location_required",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "validation_rules",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "dimensions_schema",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
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
        sa.ForeignKeyConstraint(
            ["canonical_source_id"],
            ["sources.id"],
            name=op.f("fk_metrics_canonical_source_id_sources"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["data_categories.id"],
            name=op.f("fk_metrics_category_id_data_categories"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_metrics")),
        sa.UniqueConstraint("slug", name=op.f("uq_metrics_slug")),
    )
    op.create_index("ix_metrics_category_id", "metrics", ["category_id"], unique=False)
    op.create_index(
        "uq_metrics_category_name",
        "metrics",
        ["category_id", "name"],
        unique=True,
    )

    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=True),
        sa.Column("level", location_level_enum, nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("country_code", sa.String(length=3), nullable=True),
        sa.Column("path", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
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
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["locations.id"],
            name=op.f("fk_locations_parent_id_locations"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_locations")),
        sa.UniqueConstraint("path", name=op.f("uq_locations_path")),
    )
    op.create_index("ix_locations_parent_id", "locations", ["parent_id"], unique=False)
    op.create_index(
        "uq_locations_parent_name_level",
        "locations",
        ["parent_id", "name", "level"],
        unique=True,
        postgresql_where=sa.text("parent_id IS NOT NULL"),
    )
    op.create_index(
        "uq_locations_root_name_level",
        "locations",
        ["name", "level"],
        unique=True,
        postgresql_where=sa.text("parent_id IS NULL"),
    )

    op.create_table(
        "scraper_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scraper_name", sa.String(length=120), nullable=False),
        sa.Column("trigger_type", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            scraper_run_status_enum,
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "records_read",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "records_inserted",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "records_updated",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "records_rejected",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "run_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
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
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["data_categories.id"],
            name=op.f("fk_scraper_runs_category_id_data_categories"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_scraper_runs_source_id_sources"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scraper_runs")),
    )

    op.create_table(
        "data_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scraper_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("supersedes_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_reference", sa.String(length=128), nullable=True),
        sa.Column("unit_override", sa.String(length=32), nullable=True),
        sa.Column(
            "value_type",
            metric_value_type_enum,
            nullable=False,
            server_default=sa.text("'numeric'"),
        ),
        sa.Column("value_numeric", sa.Numeric(24, 8), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_boolean", sa.Boolean(), nullable=True),
        sa.Column(
            "extra_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "ingestion_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "version_no",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "is_current",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "is_valid",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "confidence_score",
            sa.Numeric(5, 4),
            nullable=False,
            server_default=sa.text("1.0000"),
        ),
        sa.Column(
            "dedupe_key",
            sa.Text(),
            sa.Computed(
                """
                md5(
                    metric_id::text || '|' ||
                    source_id::text || '|' ||
                    coalesce(location_id::text, 'global') || '|' ||
                    recorded_at::text || '|' ||
                    coalesce(external_reference, '')
                )
                """,
                persisted=True,
            ),
            nullable=False,
        ),
        sa.CheckConstraint(
            """
            (CASE WHEN value_numeric IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN value_text IS NOT NULL THEN 1 ELSE 0 END) +
            (CASE WHEN value_boolean IS NOT NULL THEN 1 ELSE 0 END) <= 1
            """,
            name=op.f("ck_data_points_single_scalar_value"),
        ),
        sa.CheckConstraint(
            """
            value_numeric IS NOT NULL OR
            value_text IS NOT NULL OR
            value_boolean IS NOT NULL OR
            extra_data <> '{}'::jsonb
            """,
            name=op.f("ck_data_points_has_payload"),
        ),
        sa.CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name=op.f("ck_data_points_confidence_score_range"),
        ),
        sa.CheckConstraint(
            "version_no >= 1",
            name=op.f("ck_data_points_version_no_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            name=op.f("fk_data_points_location_id_locations"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["metric_id"],
            ["metrics.id"],
            name=op.f("fk_data_points_metric_id_metrics"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["scraper_run_id"],
            ["scraper_runs.id"],
            name=op.f("fk_data_points_scraper_run_id_scraper_runs"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_data_points_source_id_sources"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_id"],
            ["data_points.id"],
            name=op.f("fk_data_points_supersedes_id_data_points"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_data_points")),
    )
    op.create_index(
        "ix_data_points_metric_recorded_at",
        "data_points",
        ["metric_id", "recorded_at"],
        unique=False,
    )
    op.create_index("ix_data_points_source_id", "data_points", ["source_id"], unique=False)
    op.create_index(
        "ix_data_points_location_id",
        "data_points",
        ["location_id"],
        unique=False,
    )
    op.create_index(
        "ix_data_points_supersedes_id",
        "data_points",
        ["supersedes_id"],
        unique=False,
    )
    op.create_index(
        "ix_data_points_source_recorded_at",
        "data_points",
        ["source_id", "recorded_at"],
        unique=False,
    )
    op.create_index(
        "ix_data_points_recorded_at",
        "data_points",
        ["recorded_at"],
        unique=False,
    )
    op.create_index(
        "ix_data_points_recorded_at_brin",
        "data_points",
        ["recorded_at"],
        unique=False,
        postgresql_using="brin",
    )
    op.create_index(
        "ix_data_points_current_metric_recorded_at",
        "data_points",
        ["metric_id", "recorded_at"],
        unique=False,
        postgresql_where=sa.text("is_current"),
    )
    op.create_index(
        "uq_data_points_dedupe_key_current",
        "data_points",
        ["dedupe_key"],
        unique=True,
        postgresql_where=sa.text("is_current"),
    )

    op.create_table(
        "ingestion_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scraper_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_point_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["data_point_id"],
            ["data_points.id"],
            name=op.f("fk_ingestion_logs_data_point_id_data_points"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["scraper_run_id"],
            ["scraper_runs.id"],
            name=op.f("fk_ingestion_logs_scraper_run_id_scraper_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingestion_logs")),
    )
    op.create_index(
        "ix_ingestion_logs_scraper_run_created_at",
        "ingestion_logs",
        ["scraper_run_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "energy_details",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_point_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("energy_type", sa.String(length=32), nullable=False),
        sa.Column("fuel_grade", sa.String(length=32), nullable=True),
        sa.Column("tariff_code", sa.String(length=32), nullable=True),
        sa.Column("customer_type", sa.String(length=32), nullable=True),
        sa.Column("provider_name", sa.String(length=120), nullable=True),
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
            ["data_point_id"],
            ["data_points.id"],
            name=op.f("fk_energy_details_data_point_id_data_points"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_energy_details")),
        sa.UniqueConstraint("data_point_id", name=op.f("uq_energy_details_data_point_id")),
    )
    op.create_index(
        "ix_energy_details_energy_type",
        "energy_details",
        ["energy_type"],
        unique=False,
    )
    op.create_index(
        "ix_energy_details_fuel_grade",
        "energy_details",
        ["fuel_grade"],
        unique=False,
    )
    op.create_index(
        "ix_energy_details_tariff_code",
        "energy_details",
        ["tariff_code"],
        unique=False,
    )

    op.create_table(
        "exchange_rate_details",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_point_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("quote_currency", sa.String(length=3), nullable=False),
        sa.Column("rate_type", sa.String(length=32), nullable=True),
        sa.Column("market", sa.String(length=32), nullable=True),
        sa.Column("inverse_rate", sa.Numeric(24, 8), nullable=True),
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
            ["data_point_id"],
            ["data_points.id"],
            name=op.f("fk_exchange_rate_details_data_point_id_data_points"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exchange_rate_details")),
        sa.UniqueConstraint(
            "data_point_id",
            name=op.f("uq_exchange_rate_details_data_point_id"),
        ),
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

    op.create_table(
        "salary_details",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_point_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_title", sa.String(length=120), nullable=True),
        sa.Column("seniority_level", sa.String(length=32), nullable=True),
        sa.Column("employment_type", sa.String(length=32), nullable=True),
        sa.Column("pay_period", sa.String(length=16), nullable=True),
        sa.Column("currency_code", sa.String(length=3), nullable=True),
        sa.Column("industry", sa.String(length=64), nullable=True),
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
            ["data_point_id"],
            ["data_points.id"],
            name=op.f("fk_salary_details_data_point_id_data_points"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_salary_details")),
        sa.UniqueConstraint("data_point_id", name=op.f("uq_salary_details_data_point_id")),
    )
    op.create_index(
        "ix_salary_details_role_title",
        "salary_details",
        ["role_title"],
        unique=False,
    )
    op.create_index(
        "ix_salary_details_seniority_level",
        "salary_details",
        ["seniority_level"],
        unique=False,
    )
    op.create_index(
        "ix_salary_details_employment_type",
        "salary_details",
        ["employment_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_salary_details_employment_type", table_name="salary_details")
    op.drop_index("ix_salary_details_seniority_level", table_name="salary_details")
    op.drop_index("ix_salary_details_role_title", table_name="salary_details")
    op.drop_table("salary_details")

    op.drop_index("ix_exchange_rate_details_market", table_name="exchange_rate_details")
    op.drop_index("ix_exchange_rate_details_pair", table_name="exchange_rate_details")
    op.drop_table("exchange_rate_details")

    op.drop_index("ix_energy_details_tariff_code", table_name="energy_details")
    op.drop_index("ix_energy_details_fuel_grade", table_name="energy_details")
    op.drop_index("ix_energy_details_energy_type", table_name="energy_details")
    op.drop_table("energy_details")

    op.drop_index(
        "ix_ingestion_logs_scraper_run_created_at",
        table_name="ingestion_logs",
    )
    op.drop_table("ingestion_logs")

    op.drop_index("uq_data_points_dedupe_key_current", table_name="data_points")
    op.drop_index(
        "ix_data_points_current_metric_recorded_at",
        table_name="data_points",
    )
    op.drop_index("ix_data_points_recorded_at_brin", table_name="data_points")
    op.drop_index("ix_data_points_recorded_at", table_name="data_points")
    op.drop_index("ix_data_points_supersedes_id", table_name="data_points")
    op.drop_index("ix_data_points_source_recorded_at", table_name="data_points")
    op.drop_index("ix_data_points_location_id", table_name="data_points")
    op.drop_index("ix_data_points_source_id", table_name="data_points")
    op.drop_index("ix_data_points_metric_recorded_at", table_name="data_points")
    op.drop_table("data_points")

    op.drop_table("scraper_runs")

    op.drop_index("uq_locations_root_name_level", table_name="locations")
    op.drop_index("uq_locations_parent_name_level", table_name="locations")
    op.drop_index("ix_locations_parent_id", table_name="locations")
    op.drop_table("locations")

    op.drop_index("uq_metrics_category_name", table_name="metrics")
    op.drop_index("ix_metrics_category_id", table_name="metrics")
    op.drop_table("metrics")

    op.drop_table("sources")
    op.drop_table("data_categories")

    scraper_run_status_enum.drop(op.get_bind(), checkfirst=True)
    location_level_enum.drop(op.get_bind(), checkfirst=True)
    metric_frequency_enum.drop(op.get_bind(), checkfirst=True)
    metric_value_type_enum.drop(op.get_bind(), checkfirst=True)
    source_type_enum.drop(op.get_bind(), checkfirst=True)
