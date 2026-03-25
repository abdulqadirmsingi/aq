"""In-memory document download with SHA-256 fingerprinting."""

from __future__ import annotations

import hashlib

from src.core.http_client import ScraperHttpClient
from src.domains.energy.ewura.exceptions import EwuraDownloadTooLargeError


def download_bytes_with_hash(
    client: ScraperHttpClient,
    url: str,
    *,
    max_bytes: int,
) -> tuple[bytes, str]:
    """
    Download ``url`` into memory; return ``(raw_bytes, sha256_hex)``.

    Never writes to disk. Raises ``EwuraDownloadTooLargeError`` when over cap.
    """
    try:
        raw = client.get_bytes_bounded(url, max_bytes)
    except ValueError as exc:
        raise EwuraDownloadTooLargeError(str(exc)) from exc
    digest = hashlib.sha256(raw).hexdigest()
    return raw, digest
