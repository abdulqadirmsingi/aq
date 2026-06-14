from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TenderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class TenderFiltersRead(BaseModel):
    tender_statuses: list[str]
    procurement_methods: list[str]
    financial_years: list[str]
    procuring_entities: list[str]
    total_published: int
    total_awarded: int
