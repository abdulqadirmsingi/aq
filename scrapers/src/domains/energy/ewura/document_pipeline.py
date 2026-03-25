"""Download cap-price bulletins (PDF or DOCX) and parse in memory."""

from __future__ import annotations

import logging

from src.core.http_client import ScraperHttpClient
from src.domains.energy.ewura.docx_pipeline import parse_cap_price_docx_bytes
from src.domains.energy.ewura.download import download_bytes_with_hash
from src.domains.energy.ewura.exceptions import EwuraDownloadTooLargeError
from src.domains.energy.ewura.models import EwuraParseOutcome, FilteredDocumentRef
from src.domains.energy.ewura.pdf_pipeline import parse_cap_price_pdf_bytes
from src.domains.energy.ewura.structured_log import ewura_extra, ewura_warning

logger = logging.getLogger(__name__)


def fetch_and_parse_cap_price_document(
    client: ScraperHttpClient,
    ref: FilteredDocumentRef,
    *,
    max_bytes: int,
) -> EwuraParseOutcome:
    """Download one bulletin and dispatch to PDF or DOCX parser."""
    url = str(ref.url)
    path = url.split("?", maxsplit=1)[0].lower()
    if not (path.endswith(".pdf") or path.endswith(".docx")):
        ewura_warning(
            logger,
            "ewura_unsupported_format",
            event="ewura_unsupported_format",
            document_url=url,
            extension=path.rsplit(".", maxsplit=1)[-1] if "." in path else "",
        )
        return EwuraParseOutcome(
            ok=False,
            document_url=url,
            error="unsupported_format",
        )

    try:
        raw, sha = download_bytes_with_hash(client, url, max_bytes=max_bytes)
    except EwuraDownloadTooLargeError as exc:
        ewura_warning(
            logger,
            "ewura_download_too_large",
            event="ewura_download_too_large",
            document_url=url,
            err=str(exc),
        )
        return EwuraParseOutcome(
            ok=False,
            document_url=url,
            error=f"download_too_large:{exc}",
        )
    except Exception as exc:
        logger.exception(
            "ewura_download_failed",
            extra=ewura_extra(event="ewura_download_failed", document_url=url),
        )
        return EwuraParseOutcome(
            ok=False,
            document_url=url,
            error=f"download_failed:{exc!s}",
        )

    if path.endswith(".pdf"):
        return parse_cap_price_pdf_bytes(
            raw,
            document_url=url,
            link_text=ref.link_text,
            content_sha256=sha,
        )
    return parse_cap_price_docx_bytes(
        raw,
        document_url=url,
        link_text=ref.link_text,
        content_sha256=sha,
    )
