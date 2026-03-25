"""Business logic for EWURA scraper run monitoring endpoints."""

from __future__ import annotations

from uuid import UUID

from app.common.pagination import Page, build_page
from app.modules.energy.repositories.fuel_monitor_repository import (
    FuelMonitorRepository,
    FuelRunLogRecord,
    FuelRunRecord,
)
from app.modules.energy.schemas.fuel_monitor import (
    EwuraFuelRunLogRead,
    EwuraFuelRunRead,
)


class FuelMonitorService:
    def __init__(self, repository: FuelMonitorRepository) -> None:
        self._repository = repository

    async def list_runs(
        self,
        *,
        limit: int,
        offset: int,
        status: str | None,
    ) -> Page[EwuraFuelRunRead]:
        rows = await self._repository.list_runs(limit=limit, offset=offset, status=status)
        total = await self._repository.count_runs(status=status)
        return build_page(
            [self._to_run(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_run(self, run_id: UUID) -> EwuraFuelRunRead | None:
        row = await self._repository.get_run(run_id)
        return None if row is None else self._to_run(row)

    async def list_run_logs(
        self,
        *,
        run_id: UUID,
        limit: int,
        offset: int,
        level: str | None,
        event_type: str | None,
    ) -> Page[EwuraFuelRunLogRead]:
        rows = await self._repository.list_run_logs(
            run_id=run_id,
            limit=limit,
            offset=offset,
            level=level,
            event_type=event_type,
        )
        total = await self._repository.count_run_logs(
            run_id=run_id,
            level=level,
            event_type=event_type,
        )
        return build_page(
            [self._to_log(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def _to_run(row: FuelRunRecord) -> EwuraFuelRunRead:
        return EwuraFuelRunRead(
            id=row.id,
            scraper_name=row.scraper_name,
            trigger_type=row.trigger_type,
            status=row.status,
            category_slug=row.category_slug,
            source_name=row.source_name,
            started_at=row.started_at,
            finished_at=row.finished_at,
            records_read=row.records_read,
            records_inserted=row.records_inserted,
            records_updated=row.records_updated,
            records_rejected=row.records_rejected,
            error_message=row.error_message,
            run_metadata=row.run_metadata,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _to_log(row: FuelRunLogRecord) -> EwuraFuelRunLogRead:
        return EwuraFuelRunLogRead(
            id=row.id,
            scraper_run_id=row.scraper_run_id,
            data_point_id=row.data_point_id,
            data_point_recorded_at=row.data_point_recorded_at,
            level=row.level,
            event_type=row.event_type,
            message=row.message,
            details=row.details,
            created_at=row.created_at,
        )
