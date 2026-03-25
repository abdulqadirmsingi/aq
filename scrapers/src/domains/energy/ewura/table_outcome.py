"""Shared assembly: extracted tables → ``EwuraParseOutcome``."""

from __future__ import annotations

import logging

from src.domains.energy.ewura.dates import extract_effective_date
from src.domains.energy.ewura.extract_data import tables_to_fuel_records
from src.domains.energy.ewura.models import EwuraDocumentPayload, EwuraParseOutcome
from src.domains.energy.ewura.records_dedupe import dedupe_fuel_records
from src.domains.energy.ewura.structured_log import (
    ewura_error,
    ewura_info,
    ewura_warning,
)

logger = logging.getLogger(__name__)


def cap_price_outcome_from_tables(
    tables: list[list[list[str | None]]],
    *,
    body_text_for_date: str,
    link_text: str,
    document_url: str,
    content_sha256: str,
    source_format: str,
) -> EwuraParseOutcome:
    """Map normalized tables to payload (date, rows, dedupe) or structured failure."""
    warnings: list[str] = []
    if not tables:
        warnings.append("no_tables_found")
        ewura_warning(
            logger,
            "ewura_no_tables",
            event="ewura_no_tables",
            document_url=document_url,
            source_format=source_format,
        )
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

    effective = extract_effective_date(link_text, body_text_for_date, document_url)
    if effective is None:
        warnings.append("effective_date_unresolved")
        ewura_warning(
            logger,
            "ewura_date_unresolved",
            event="ewura_date_unresolved",
            document_url=document_url,
            source_format=source_format,
        )
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
    records = dedupe_fuel_records(records)
    if not records:
        ewura_warning(
            logger,
            "ewura_no_fuel_rows",
            event="ewura_no_fuel_rows",
            document_url=document_url,
            source_format=source_format,
        )
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
    ewura_info(
        logger,
        "ewura_parse_ok",
        event="ewura_parse_ok",
        document_url=document_url,
        source_format=source_format,
        record_count=len(records),
        warning_count=len(warnings),
    )
    return EwuraParseOutcome(ok=True, document_url=document_url, payload=payload)


def log_parse_exception(
    *,
    document_url: str,
    content_sha256: str,
    exc: BaseException,
    source_format: str,
) -> EwuraParseOutcome:
    ewura_error(
        logger,
        "ewura_open_failed",
        event="ewura_open_failed",
        document_url=document_url,
        source_format=source_format,
        error=str(exc),
    )
    return EwuraParseOutcome(
        ok=False,
        document_url=document_url,
        error=f"{source_format}_read_failed:{exc!s}",
        payload=EwuraDocumentPayload(
            document_url=document_url,
            published_date=None,
            data=[],
            content_sha256=content_sha256,
            parse_warnings=[f"{source_format}_read_failed:{exc!s}"],
        ),
    )
