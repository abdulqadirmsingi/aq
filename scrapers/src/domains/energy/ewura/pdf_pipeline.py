"""End-to-end PDF bytes → structured cap-price payload."""

from __future__ import annotations

import logging

from src.core.http_client import ScraperHttpClient
from src.domains.energy.ewura.dates import extract_effective_date
from src.domains.energy.ewura.download import download_bytes_with_hash
from src.domains.energy.ewura.exceptions import EwuraDownloadTooLargeError
from src.domains.energy.ewura.extract_data import tables_to_fuel_records
from src.domains.energy.ewura.models import (
    EwuraDocumentPayload,
    EwuraParseOutcome,
    FilteredDocumentRef,
)
from src.domains.energy.ewura.pdf_tables import extract_tables_from_pdf

logger = logging.getLogger(__name__)


def parse_cap_price_pdf_bytes(
    pdf_bytes: bytes,
    *,
    document_url: str,
    link_text: str,
    content_sha256: str,
) -> EwuraParseOutcome:
    """Parse in-memory PDF; no disk I/O."""
    warnings: list[str] = []
    try:
        tables, first_page_text = extract_tables_from_pdf(pdf_bytes)
    except Exception as exc:
        logger.exception("ewura_pdf_open_failed", extra={"url": document_url})
        return EwuraParseOutcome(
            ok=False,
            document_url=document_url,
            error=f"pdf_read_failed:{exc!s}",
            payload=EwuraDocumentPayload(
                document_url=document_url,
                published_date=None,
                data=[],
                content_sha256=content_sha256,
                parse_warnings=[f"pdf_read_failed:{exc!s}"],
            ),
        )

    if not tables:
        warnings.append("no_tables_found")
        return EwuraParseOutcome(
            ok=False,
            document_url=document_url,
            error="no_tables_found",
            payload=EwuraDocumentPayload(
                document_url=document_url,
                published_date=None,
                data=[],
                content_sha256=content_sha256,
                parse_warnings=warnings,
            ),
        )

    effective = extract_effective_date(link_text, first_page_text, document_url)
    if effective is None:
        warnings.append("effective_date_unresolved")
        return EwuraParseOutcome(
            ok=False,
            document_url=document_url,
            error="effective_date_unresolved",
            payload=EwuraDocumentPayload(
                document_url=document_url,
                published_date=None,
                data=[],
                content_sha256=content_sha256,
                parse_warnings=warnings,
            ),
        )

    records, table_warnings = tables_to_fuel_records(
        tables,
        effective_date=effective,
    )
    warnings.extend(table_warnings)
    if not records:
        return EwuraParseOutcome(
            ok=False,
            document_url=document_url,
            error="no_fuel_rows",
            payload=EwuraDocumentPayload(
                document_url=document_url,
                published_date=effective.isoformat(),
                data=[],
                content_sha256=content_sha256,
                parse_warnings=warnings,
            ),
        )

    payload = EwuraDocumentPayload(
        document_url=document_url,
        published_date=effective.isoformat(),
        data=records,
        content_sha256=content_sha256,
        parse_warnings=warnings,
    )
    return EwuraParseOutcome(ok=True, document_url=document_url, payload=payload)


def fetch_and_parse_cap_price_pdf(
    client: ScraperHttpClient,
    ref: FilteredDocumentRef,
    *,
    max_bytes: int,
) -> EwuraParseOutcome:
    """Download (in-memory) and parse one cap-price PDF."""
    url = str(ref.url)
    path = url.split("?", maxsplit=1)[0].lower()
    if not path.endswith(".pdf"):
        return EwuraParseOutcome(
            ok=False,
            document_url=url,
            error="unsupported_non_pdf",
        )

    try:
        raw, sha = download_bytes_with_hash(client, url, max_bytes=max_bytes)
    except EwuraDownloadTooLargeError as exc:
        logger.warning("ewura_download_too_large", extra={"url": url, "err": str(exc)})
        return EwuraParseOutcome(
            ok=False,
            document_url=url,
            error=f"download_too_large:{exc}",
        )
    except Exception as exc:
        logger.exception("ewura_download_failed", extra={"url": url})
        return EwuraParseOutcome(
            ok=False,
            document_url=url,
            error=f"download_failed:{exc!s}",
        )

    return parse_cap_price_pdf_bytes(
        raw,
        document_url=url,
        link_text=ref.link_text,
        content_sha256=sha,
    )
