"""EWURA petroleum cap-price ingestion (listing → parse → persist)."""

from src.domains.energy.ewura.fetch import fetch_page
from src.domains.energy.ewura.filters import filter_documents
from src.domains.energy.ewura.links import extract_document_links
from src.domains.energy.ewura.listing import list_cap_price_documents_from_html
from src.domains.energy.ewura.models import DocumentLink, FilteredDocumentRef

__all__ = [
    "DocumentLink",
    "FilteredDocumentRef",
    "extract_document_links",
    "fetch_page",
    "filter_documents",
    "list_cap_price_documents_from_html",
]
