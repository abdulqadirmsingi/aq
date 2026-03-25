"""In-memory DOCX → tables (python-docx only)."""

from __future__ import annotations

import logging

from src.domains.energy.ewura.docx_tables import extract_tables_from_docx
from src.domains.energy.ewura.models import EwuraParseOutcome
from src.domains.energy.ewura.structured_log import ewura_extra
from src.domains.energy.ewura.table_outcome import (
    cap_price_outcome_from_tables,
    log_parse_exception,
)

logger = logging.getLogger(__name__)


def parse_cap_price_docx_bytes(
    docx_bytes: bytes,
    *,
    document_url: str,
    link_text: str,
    content_sha256: str,
) -> EwuraParseOutcome:
    """Parse in-memory DOCX; no disk I/O."""
    try:
        tables, paragraph_text = extract_tables_from_docx(docx_bytes)
    except Exception as exc:
        logger.exception(
            "ewura_docx_open_failed",
            extra=ewura_extra(
                event="ewura_docx_open_failed",
                document_url=document_url,
            ),
        )
        return log_parse_exception(
            document_url=document_url,
            content_sha256=content_sha256,
            exc=exc,
            source_format="docx",
        )

    return cap_price_outcome_from_tables(
        tables,
        body_text_for_date=paragraph_text,
        link_text=link_text,
        document_url=document_url,
        content_sha256=content_sha256,
        source_format="docx",
    )
