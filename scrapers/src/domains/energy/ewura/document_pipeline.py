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


def _document_extension(url: str) -> str | None:
    path = url.split("?", maxsplit=1)[0].lower()
    if path.endswith(".pdf"):
        return ".pdf"
    if path.endswith(".docx"):
        return ".docx"
    return None


def download_cap_price_bulletin(
    client: ScraperHttpClient,
    ref: FilteredDocumentRef,
    *,
    max_bytes: int,
) -> EwuraParseOutcome | tuple[bytes, str, str]:
    """
    Download raw bytes and fingerprint, or return an error outcome.

    Success: ``(raw_bytes, sha256_hex, extension)`` where extension is
    ``.pdf`` or ``.docx``.
    """
    url = str(ref.url)
    ext = _document_extension(url)
    if ext is None:
        path = url.split("?", maxsplit=1)[0].lower()
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

    return (raw, sha, ext)


def parse_cap_price_bulletin_bytes(
    raw: bytes,
    ext: str,
    ref: FilteredDocumentRef,
    content_sha256: str,
) -> EwuraParseOutcome:
    """Parse already-downloaded bulletin bytes."""
    url = str(ref.url)
    if ext == ".pdf":
        return parse_cap_price_pdf_bytes(
            raw,
            document_url=url,
            link_text=ref.link_text,
            content_sha256=content_sha256,
        )
    if ext == ".docx":
        return parse_cap_price_docx_bytes(
            raw,
            document_url=url,
            link_text=ref.link_text,
            content_sha256=content_sha256,
        )
    return EwuraParseOutcome(
        ok=False,
        document_url=url,
        error="unsupported_format",
    )


def fetch_and_parse_cap_price_document(
    client: ScraperHttpClient,
    ref: FilteredDocumentRef,
    *,
    max_bytes: int,
) -> EwuraParseOutcome:
    """Download one bulletin and dispatch to PDF or DOCX parser."""
    step = download_cap_price_bulletin(client, ref, max_bytes=max_bytes)
    if isinstance(step, EwuraParseOutcome):
        return step
    raw, sha, ext = step
    return parse_cap_price_bulletin_bytes(raw, ext, ref, sha)
