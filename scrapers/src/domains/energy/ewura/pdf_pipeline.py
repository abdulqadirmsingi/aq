"""In-memory PDF → tables (pdfplumber only)."""

from __future__ import annotations

import logging

from src.domains.energy.ewura.models import EwuraParseOutcome
from src.domains.energy.ewura.pdf_tables import extract_tables_from_pdf
from src.domains.energy.ewura.structured_log import ewura_extra
from src.domains.energy.ewura.table_outcome import (
    cap_price_outcome_from_tables,
    log_parse_exception,
)

logger = logging.getLogger(__name__)


def parse_cap_price_pdf_bytes(
    pdf_bytes: bytes,
    *,
    document_url: str,
    link_text: str,
    content_sha256: str,
) -> EwuraParseOutcome:
    """Parse in-memory PDF; no disk I/O."""
    try:
        tables, first_page_text = extract_tables_from_pdf(pdf_bytes)
    except Exception as exc:
        logger.exception(
            "ewura_pdf_open_failed",
            extra=ewura_extra(
                event="ewura_pdf_open_failed",
                document_url=document_url,
            ),
        )
        return log_parse_exception(
            document_url=document_url,
            content_sha256=content_sha256,
            exc=exc,
            source_format="pdf",
        )

    return cap_price_outcome_from_tables(
        tables,
        body_text_for_date=first_page_text,
        link_text=link_text,
        document_url=document_url,
        content_sha256=content_sha256,
        source_format="pdf",
    )
