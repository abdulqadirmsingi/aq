from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.procurement.models.tender import ProcurementTender


@dataclass(frozen=True)
class TenderRecord:
    id: uuid.UUID
    ocid: str
    tender_reference: str
    title: str
    description: str | None
    procuring_entity_name: str | None
    procuring_entity_id: str | None
    procurement_method: str | None
    procurement_method_details: str | None
    tender_status: str | None
    tender_value_amount: Decimal | None
    tender_value_currency: str | None
    tender_period_start: datetime | None
    tender_period_end: datetime | None
    has_award: bool
    award_date: datetime | None
    award_value_amount: Decimal | None
    award_value_currency: str | None
    contractor_name: str | None
    contractor_id: str | None
    financial_year: str | None
    location: str | None
    source_url: str | None
    fetched_at: datetime
    created_at: datetime
    updated_at: datetime


class TenderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_tenders(
        self,
        *,
        tender_status: str | None = None,
        has_award: bool | None = None,
        procurement_method: str | None = None,
        procuring_entity_id: str | None = None,
        financial_year: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProcurementTender]:
        stmt = select(ProcurementTender).where(
            *_build_filters(
                tender_status=tender_status,
                has_award=has_award,
                procurement_method=procurement_method,
                procuring_entity_id=procuring_entity_id,
                financial_year=financial_year,
                search=search,
            )
        )
        stmt = stmt.order_by(
            ProcurementTender.tender_period_end.desc().nulls_last(),
            ProcurementTender.fetched_at.desc(),
        ).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_tenders(
        self,
        *,
        tender_status: str | None = None,
        has_award: bool | None = None,
        procurement_method: str | None = None,
        procuring_entity_id: str | None = None,
        financial_year: str | None = None,
        search: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(ProcurementTender).where(
            *_build_filters(
                tender_status=tender_status,
                has_award=has_award,
                procurement_method=procurement_method,
                procuring_entity_id=procuring_entity_id,
                financial_year=financial_year,
                search=search,
            )
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def get_by_id(self, tender_id: uuid.UUID) -> ProcurementTender | None:
        result = await self._session.execute(
            select(ProcurementTender).where(ProcurementTender.id == tender_id)
        )
        return result.scalar_one_or_none()

    async def list_distinct_statuses(self) -> list[str]:
        result = await self._session.execute(
            select(ProcurementTender.tender_status)
            .where(ProcurementTender.tender_status.isnot(None))
            .distinct()
            .order_by(ProcurementTender.tender_status)
        )
        return [row[0] for row in result]

    async def list_distinct_methods(self) -> list[str]:
        result = await self._session.execute(
            select(ProcurementTender.procurement_method)
            .where(ProcurementTender.procurement_method.isnot(None))
            .distinct()
            .order_by(ProcurementTender.procurement_method)
        )
        return [row[0] for row in result]

    async def list_distinct_financial_years(self) -> list[str]:
        result = await self._session.execute(
            select(ProcurementTender.financial_year)
            .where(ProcurementTender.financial_year.isnot(None))
            .distinct()
            .order_by(ProcurementTender.financial_year.desc())
        )
        return [row[0] for row in result]

    async def list_distinct_procuring_entities(self) -> list[str]:
        result = await self._session.execute(
            select(ProcurementTender.procuring_entity_name)
            .where(ProcurementTender.procuring_entity_name.isnot(None))
            .distinct()
            .order_by(ProcurementTender.procuring_entity_name)
        )
        return [row[0] for row in result]

    async def count_published(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(ProcurementTender).where(
                ProcurementTender.tender_status == "active"
            )
        )
        return int(result.scalar_one())

    async def count_awarded(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(ProcurementTender).where(
                ProcurementTender.has_award.is_(True)
            )
        )
        return int(result.scalar_one())


def _build_filters(
    *,
    tender_status: str | None,
    has_award: bool | None,
    procurement_method: str | None,
    procuring_entity_id: str | None,
    financial_year: str | None,
    search: str | None,
) -> list:
    conditions = []
    if tender_status is not None:
        conditions.append(ProcurementTender.tender_status == tender_status)
    if has_award is not None:
        conditions.append(ProcurementTender.has_award.is_(has_award))
    if procurement_method is not None:
        conditions.append(ProcurementTender.procurement_method == procurement_method)
    if procuring_entity_id is not None:
        conditions.append(ProcurementTender.procuring_entity_id == procuring_entity_id)
    if financial_year is not None:
        conditions.append(ProcurementTender.financial_year == financial_year)
    if search is not None:
        pattern = f"%{search}%"
        conditions.append(
            or_(
                ProcurementTender.title.ilike(pattern),
                ProcurementTender.procuring_entity_name.ilike(pattern),
                ProcurementTender.tender_reference.ilike(pattern),
            )
        )
    return conditions
