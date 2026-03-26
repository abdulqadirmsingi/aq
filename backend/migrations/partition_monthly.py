"""Helpers for monthly RANGE partitions on data_points.recorded_at."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date

import sqlalchemy as sa
from alembic import op


def iter_month_starts(first: date, last: date) -> Iterator[tuple[date, date]]:
    """Yield (month_start, next_month_start) for each month from first through last (inclusive)."""
    start_norm = date(first.year, first.month, 1)
    end_norm = date(last.year, last.month, 1)
    y, m = start_norm.year, start_norm.month
    while (y, m) <= (end_norm.year, end_norm.month):
        month_start = date(y, m, 1)
        if m == 12:
            next_month_start = date(y + 1, 1, 1)
        else:
            next_month_start = date(y, m + 1, 1)
        yield month_start, next_month_start
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1


def partition_table_name(month_start: date) -> str:
    return f"data_points_{month_start.year}_{month_start.month:02d}"


def create_monthly_partitions(
    *,
    first_month: date,
    last_month: date,
) -> None:
    """Attach monthly partitions (data_points_YYYY_MM) plus DEFAULT for out-of-range rows."""
    for month_start, next_month_start in iter_month_starts(first_month, last_month):
        name = partition_table_name(month_start)
        op.execute(
            sa.text(
                f'CREATE TABLE "{name}" PARTITION OF data_points '
                f"FOR VALUES FROM ('{month_start.isoformat()}') "
                f"TO ('{next_month_start.isoformat()}')"
            )
        )
    op.execute(
        sa.text("CREATE TABLE data_points_default PARTITION OF data_points DEFAULT")
    )


def drop_monthly_partitions(
    *,
    first_month: date,
    last_month: date,
) -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS data_points_default"))
    months = list(iter_month_starts(first_month, last_month))
    for month_start, _ in reversed(months):
        name = partition_table_name(month_start)
        op.execute(sa.text(f'DROP TABLE IF EXISTS "{name}"'))


def default_partition_range() -> tuple[date, date]:
    """First and last month (inclusive) to pre-create around the current date."""
    today = date.today()
    first = date(today.year - 2, 1, 1)
    last = date(today.year + 2, 12, 1)
    return first, last
