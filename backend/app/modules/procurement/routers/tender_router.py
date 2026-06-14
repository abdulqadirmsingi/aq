"""Procurement tender endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.pagination import Page
from app.db.session import get_db_session
from app.modules.procurement.repositories.tender_repository import TenderRepository
from app.modules.procurement.schemas.tender import TenderFiltersRead, TenderRead
from app.modules.procurement.services.tender_service import TenderService

router = APIRouter(prefix="/procurement", tags=["procurement"])


def _service(db: AsyncSession) -> TenderService:
    return TenderService(TenderRepository(db))


@router.get("/tenders", response_model=Page[TenderRead])
async def list_tenders(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    tender_status: Annotated[str | None, Query()] = None,
    has_award: Annotated[bool | None, Query()] = None,
    procurement_method: Annotated[str | None, Query()] = None,
    procuring_entity_id: Annotated[str | None, Query()] = None,
    financial_year: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query(min_length=2, max_length=200)] = None,
) -> Page[TenderRead]:
    return await _service(db).list_tenders(
        tender_status=tender_status,
        has_award=has_award,
        procurement_method=procurement_method,
        procuring_entity_id=procuring_entity_id,
        financial_year=financial_year,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.get("/tenders/filters", response_model=TenderFiltersRead)
async def get_tender_filters(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenderFiltersRead:
    return await _service(db).get_filters()


@router.get("/tenders/{tender_id}", response_model=TenderRead)
async def get_tender(
    tender_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenderRead:
    result = await _service(db).get_tender(tender_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")
    return result
