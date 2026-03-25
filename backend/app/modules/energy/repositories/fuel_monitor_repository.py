"""Data access for EWURA scraper runs and ingestion logs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ingestion import IngestionLog, ScraperRun
from app.db.models.reference import DataCategory, Source


@dataclass(frozen=True)
class FuelRunRecord:
    id: UUID
    scraper_name: str
    trigger_type: str
    status: str
    category_slug: str | None
    source_name: str | None
    started_at: datetime | None
    finished_at: datetime | None
    records_read: int
    records_inserted: int
    records_updated: int
    records_rejected: int
    error_message: str | None
    run_metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class FuelRunLogRecord:
    id: UUID
    scraper_run_id: UUID
    data_point_id: UUID | None
    data_point_recorded_at: datetime | None
    level: str
    event_type: str
    message: str
    details: dict[str, Any]
    created_at: datetime


class FuelMonitorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_runs(
        self,
        *,
        limit: int,
        offset: int,
        status: str | None = None,
    ) -> list[FuelRunRecord]:
        stmt = self._run_select().order_by(ScraperRun.created_at.desc()).limit(limit).offset(offset)
        if status is not None:
            stmt = stmt.where(ScraperRun.status == status)
        result = await self._session.execute(stmt)
        return [self._to_run_record(row._mapping) for row in result]

    async def count_runs(self, *, status: str | None = None) -> int:
        stmt = select(func.count(ScraperRun.id)).where(ScraperRun.scraper_name == "ewura_fuel")
        if status is not None:
            stmt = stmt.where(ScraperRun.status == status)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def get_run(self, run_id: UUID) -> FuelRunRecord | None:
        result = await self._session.execute(self._run_select().where(ScraperRun.id == run_id))
        row = result.first()
        return None if row is None else self._to_run_record(row._mapping)

    async def list_run_logs(
        self,
        *,
        run_id: UUID,
        limit: int,
        offset: int,
        level: str | None = None,
        event_type: str | None = None,
    ) -> list[FuelRunLogRecord]:
        stmt = (
            select(
                IngestionLog.id,
                IngestionLog.scraper_run_id,
                IngestionLog.data_point_id,
                IngestionLog.data_point_recorded_at,
                IngestionLog.level,
                IngestionLog.event_type,
                IngestionLog.message,
                IngestionLog.details,
                IngestionLog.created_at,
            )
            .where(IngestionLog.scraper_run_id == run_id)
            .order_by(IngestionLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if level is not None:
            stmt = stmt.where(IngestionLog.level == level)
        if event_type is not None:
            stmt = stmt.where(IngestionLog.event_type == event_type)
        result = await self._session.execute(stmt)
        return [self._to_log_record(row._mapping) for row in result]

    async def count_run_logs(
        self,
        *,
        run_id: UUID,
        level: str | None = None,
        event_type: str | None = None,
    ) -> int:
        stmt = select(func.count(IngestionLog.id)).where(IngestionLog.scraper_run_id == run_id)
        if level is not None:
            stmt = stmt.where(IngestionLog.level == level)
        if event_type is not None:
            stmt = stmt.where(IngestionLog.event_type == event_type)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    @staticmethod
    def _run_select():
        return (
            select(
                ScraperRun.id,
                ScraperRun.scraper_name,
                ScraperRun.trigger_type,
                ScraperRun.status,
                DataCategory.slug.label("category_slug"),
                Source.name.label("source_name"),
                ScraperRun.started_at,
                ScraperRun.finished_at,
                ScraperRun.records_read,
                ScraperRun.records_inserted,
                ScraperRun.records_updated,
                ScraperRun.records_rejected,
                ScraperRun.error_message,
                ScraperRun.run_metadata,
                ScraperRun.created_at,
                ScraperRun.updated_at,
            )
            .select_from(ScraperRun)
            .outerjoin(DataCategory, ScraperRun.category_id == DataCategory.id)
            .outerjoin(Source, ScraperRun.source_id == Source.id)
            .where(ScraperRun.scraper_name == "ewura_fuel")
        )

    @staticmethod
    def _to_run_record(row: Any) -> FuelRunRecord:
        status = row["status"]
        return FuelRunRecord(
            id=row["id"],
            scraper_name=row["scraper_name"],
            trigger_type=row["trigger_type"],
            status=status.value if isinstance(status, Enum) else str(status),
            category_slug=row["category_slug"],
            source_name=row["source_name"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            records_read=row["records_read"],
            records_inserted=row["records_inserted"],
            records_updated=row["records_updated"],
            records_rejected=row["records_rejected"],
            error_message=row["error_message"],
            run_metadata=row["run_metadata"] or {},
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _to_log_record(row: Any) -> FuelRunLogRecord:
        return FuelRunLogRecord(
            id=row["id"],
            scraper_run_id=row["scraper_run_id"],
            data_point_id=row["data_point_id"],
            data_point_recorded_at=row["data_point_recorded_at"],
            level=row["level"],
            event_type=row["event_type"],
            message=row["message"],
            details=row["details"] or {},
            created_at=row["created_at"],
        )
