"""Cursor-paginated OCDS release/record fetcher for the NeST PPRA gateway API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from src.core.retry import http_retry

logger = logging.getLogger(__name__)

# Headers required by the gateway — it validates Origin against CORS policy
_GATEWAY_HEADERS = {
    "Accept": "application/json",
    "Origin": "https://data.nest.go.tz",
    "Referer": "https://data.nest.go.tz/",
    "User-Agent": "AQ-DataIntelligenceHub/1.0 (research; contact: admin@local)",
}

# Records endpoint requires a `since` date; any date returns the same limited
# public sample, so we use the earliest available period.
_RECORDS_SINCE = "2023-07-01T00:00:00Z"


class NestOcdsApiClient:
    """Fetch OCDS tenders from the NeST PPRA gateway.

    Prioritises compiled records (full award/contract data) and supplements
    with individual releases (broader coverage, no awards).
    """

    def __init__(self, base_url: str, *, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            headers=_GATEWAY_HEADERS,
            timeout=timeout,
            follow_redirects=True,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fetch_all_records(self) -> list[dict[str, Any]]:
        """Return one dict per unique OCID.

        Compiled records (with awards/contracts) override plain releases for
        the same OCID.  All dicts are parseable by ``parse_ocds_record``.
        """
        by_ocid: dict[str, dict[str, Any]] = {}

        # 1. Broad coverage: individual releases
        releases = self._fetch_all_releases()
        by_ocid.update(releases)
        logger.info("Releases total: %d unique OCIDs", len(releases))

        # 2. Rich data: compiled records (limited public set)
        compiled = self._fetch_compiled_records()
        by_ocid.update(compiled)  # compiled overrides plain releases
        logger.info(
            "After compiled records: %d unique OCIDs total", len(by_ocid)
        )

        return list(by_ocid.values())

    def close(self) -> None:
        self._client.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_all_releases(self) -> dict[str, dict[str, Any]]:
        """Walk all cursor pages, keeping the latest release per OCID."""
        by_ocid: dict[str, dict[str, Any]] = {}
        next_url: str | None = f"{self._base_url}/releases?cursor=0"
        page = 0

        while next_url:
            try:
                data = self._get_json(next_url)
            except httpx.HTTPStatusError as exc:
                # The API has a known bug where some cursor positions return 500.
                # Stop pagination and keep what we have so far.
                logger.warning(
                    "Stopping releases pagination at page %d (server error %s): %s",
                    page + 1,
                    exc.response.status_code,
                    next_url,
                )
                break

            releases: list[dict[str, Any]] = data.get("releases") or []
            page += 1
            logger.info("Releases page %d: %d items", page, len(releases))

            for release in releases:
                ocid = release.get("ocid")
                if not ocid:
                    continue
                existing = by_ocid.get(ocid)
                if not existing or release.get("date", "") >= existing.get("date", ""):
                    by_ocid[ocid] = release

            candidate = (data.get("links") or {}).get("next")
            # Guard against circular / non-advancing next links
            next_url = candidate if (candidate and candidate != next_url) else None

        return by_ocid

    def _fetch_compiled_records(self) -> dict[str, dict[str, Any]]:
        """Fetch compiled OCDS records (small public dataset with award data)."""
        by_ocid: dict[str, dict[str, Any]] = {}
        try:
            url = f"{self._base_url}/records?cursor=0&since={_RECORDS_SINCE}"
            data = self._get_json(url)
            for record in data.get("records") or []:
                ocid = record.get("ocid")
                if ocid:
                    by_ocid[ocid] = record
            logger.info("Compiled records: %d", len(by_ocid))
        except Exception:
            logger.warning("Could not fetch compiled records; skipping", exc_info=True)
        return by_ocid

    @http_retry()
    def _get_json(self, url: str) -> dict[str, Any]:
        resp = self._client.get(url)
        resp.raise_for_status()
        return resp.json()
