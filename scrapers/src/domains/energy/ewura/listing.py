"""Orchestrate listing-stage steps (no document downloads)."""

from src.domains.energy.ewura.filters import filter_documents
from src.domains.energy.ewura.links import extract_document_links
from src.domains.energy.ewura.models import FilteredDocumentRef


def list_cap_price_documents_from_html(
    html: str,
    page_url: str,
) -> list[FilteredDocumentRef]:
    """Extract and filter PDF/DOCX cap-price links from listing HTML."""
    links = extract_document_links(html, page_url)
    return filter_documents(links)
