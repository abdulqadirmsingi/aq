"""EWURA petroleum cap-price ingestion (listing → parse → persist)."""

from src.domains.energy.ewura.fetch import fetch_page
from src.domains.energy.ewura.filters import filter_documents
from src.domains.energy.ewura.links import extract_document_links
from src.domains.energy.ewura.listing import list_cap_price_documents_from_html
from src.domains.energy.ewura.models import (
    DocumentLink,
    EwuraDocumentPayload,
    EwuraParseOutcome,
    FilteredDocumentRef,
    FuelPriceRecord,
)
from src.domains.energy.ewura.pdf_pipeline import (
    fetch_and_parse_cap_price_pdf,
    parse_cap_price_pdf_bytes,
)

__all__ = [
    "DocumentLink",
    "EwuraDocumentPayload",
    "EwuraParseOutcome",
    "FilteredDocumentRef",
    "FuelPriceRecord",
    "extract_document_links",
    "fetch_and_parse_cap_price_pdf",
    "fetch_page",
    "filter_documents",
    "list_cap_price_documents_from_html",
    "parse_cap_price_pdf_bytes",
]
