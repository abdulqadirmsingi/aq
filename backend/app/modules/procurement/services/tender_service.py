from __future__ import annotations

import uuid

from app.common.pagination import Page, build_page
from app.modules.procurement.repositories.tender_repository import TenderRepository
from app.modules.procurement.schemas.tender import TenderFiltersRead, TenderRead


class TenderService:
    def __init__(self, repository: TenderRepository) -> None:
        self._repository = repository

    async def list_tenders(
        self,
        *,
        tender_status: str | None,
        has_award: bool | None,
        procurement_method: str | None,
        procuring_entity_id: str | None,
        financial_year: str | None,
        search: str | None,
        limit: int,
        offset: int,
    ) -> Page[TenderRead]:
        filter_kwargs = dict(
            tender_status=tender_status,
            has_award=has_award,
            procurement_method=procurement_method,
            procuring_entity_id=procuring_entity_id,
            financial_year=financial_year,
            search=search,
        )
        rows, total = await _fetch_list_and_count(
            self._repository,
            filter_kwargs=filter_kwargs,
            limit=limit,
            offset=offset,
        )
        return build_page(
            [TenderRead.model_validate(row) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_tender(self, tender_id: uuid.UUID) -> TenderRead | None:
        row = await self._repository.get_by_id(tender_id)
        if row is None:
            return None
        return TenderRead.model_validate(row)

    async def get_filters(self) -> TenderFiltersRead:
        statuses, methods, years, entities, total_pub, total_awarded = (
            await _fetch_filter_data(self._repository)
        )
        return TenderFiltersRead(
            tender_statuses=statuses,
            procurement_methods=methods,
            financial_years=years,
            procuring_entities=entities,
            total_published=total_pub,
            total_awarded=total_awarded,
        )


async def _fetch_list_and_count(
    repo: TenderRepository,
    *,
    filter_kwargs: dict,
    limit: int,
    offset: int,
) -> tuple[list, int]:
    rows = await repo.list_tenders(**filter_kwargs, limit=limit, offset=offset)
    total = await repo.count_tenders(**filter_kwargs)
    return rows, total


async def _fetch_filter_data(
    repo: TenderRepository,
) -> tuple[list[str], list[str], list[str], list[str], int, int]:
    statuses = await repo.list_distinct_statuses()
    methods = await repo.list_distinct_methods()
    years = await repo.list_distinct_financial_years()
    entities = await repo.list_distinct_procuring_entities()
    total_pub = await repo.count_published()
    total_awarded = await repo.count_awarded()
    return statuses, methods, years, entities, total_pub, total_awarded
