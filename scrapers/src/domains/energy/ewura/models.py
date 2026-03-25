"""Pydantic models for EWURA listing pipeline (Phase 1)."""

from pydantic import BaseModel, Field, HttpUrl


class DocumentLink(BaseModel):
    """A PDF or DOCX hyperlink discovered on the listing page."""

    url: HttpUrl
    link_text: str = Field(default="", max_length=2000)


class FilteredDocumentRef(BaseModel):
    """Cap-price document after keyword and path filtering."""

    url: HttpUrl
    link_text: str = Field(default="", max_length=2000)
