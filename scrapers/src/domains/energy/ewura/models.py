"""Pydantic models for EWURA listing and parsed fuel payloads."""

from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class DocumentLink(BaseModel):
    """A PDF or DOCX hyperlink discovered on the listing page."""

    url: HttpUrl
    link_text: str = Field(default="", max_length=2000)


class FilteredDocumentRef(BaseModel):
    """Cap-price document after keyword and path filtering."""

    url: HttpUrl
    link_text: str = Field(default="", max_length=2000)


FuelType = Literal["petrol", "diesel", "kerosene"]


class FuelPriceRecord(BaseModel):
    """One observation per location and fuel type (retail cap)."""

    location: str = Field(max_length=200)
    fuel_type: FuelType
    price: int = Field(ge=0)
    unit: str = Field(default="TZS/Litre", max_length=32)
    recorded_at: date


class EwuraDocumentPayload(BaseModel):
    """Structured extraction result for one EWURA bulletin."""

    source: Literal["EWURA"] = "EWURA"
    source_id: UUID | None = None
    document_url: str
    published_date: str | None = Field(
        default=None,
        description="Effective date YYYY-MM-DD when resolved",
    )
    data: list[FuelPriceRecord] = Field(default_factory=list)
    content_sha256: str = Field(min_length=64, max_length=64)
    parse_warnings: list[str] = Field(default_factory=list)


class EwuraParseOutcome(BaseModel):
    """Per-document result; ``ok`` false means skip without aborting the run."""

    ok: bool
    document_url: str
    payload: EwuraDocumentPayload | None = None
    error: str | None = None
    skipped: bool = Field(
        default=False,
        description="True when dedupe skipped download/parse for this URL or hash",
    )
