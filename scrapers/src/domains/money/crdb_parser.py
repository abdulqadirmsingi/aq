"""CRDB forex table parser."""

from __future__ import annotations

from hashlib import sha256

from bs4 import BeautifulSoup

from src.domains.money.fx_models import (
    ExchangeRateDetailPayload,
    NormalizedFxObservation,
)
from src.domains.money.fx_utils import (
    build_external_reference,
    compute_inverse_rate,
    parse_decimal_number,
    parse_source_timestamp,
)

_CRDB_METRIC_SLUGS: dict[str, str] = {
    "buy": "fx_buy_rate",
    "sell": "fx_sell_rate",
}


def parse_crdb_forex_html(
    html: str,
    *,
    source_url: str,
) -> list[NormalizedFxObservation]:
    soup = BeautifulSoup(html, "lxml")
    forex_table = soup.select_one("#forexTable")
    if forex_table is None:
        raise ValueError("CRDB forex table container not found.")

    last_updated_text = forex_table.get_text(" ", strip=True)
    if "Last Updated:" not in last_updated_text:
        raise ValueError("CRDB last-updated timestamp not found.")
    raw_last_updated = last_updated_text.split("Last Updated:", maxsplit=1)[1].split(
        "CURRENCY", maxsplit=1
    )[0].strip()
    source_last_updated_at = parse_source_timestamp(raw_last_updated)
    source_effective_date = source_last_updated_at.date()

    table = forex_table.select_one("table")
    if table is None:
        raise ValueError("CRDB forex table not found.")

    observations: list[NormalizedFxObservation] = []
    content_sha256 = sha256(html.encode("utf-8")).hexdigest()
    for row_index, row in enumerate(table.select("tbody tr"), start=1):
        cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
        if len(cells) < 4:
            continue

        instrument_name = cells[0]
        instrument_code = cells[1].upper()
        for rate_kind, value in (
            ("buy", parse_decimal_number(cells[2])),
            ("sell", parse_decimal_number(cells[3])),
        ):
            metric_slug = _CRDB_METRIC_SLUGS[rate_kind]
            detail = ExchangeRateDetailPayload(
                instrument_code=instrument_code,
                instrument_name=instrument_name,
                instrument_type="currency",
                quote_code="TZS",
                rate_kind=rate_kind,
                market_scope="commercial_bank",
                channel="counter",
                source_effective_date=source_effective_date,
                source_last_updated_at=source_last_updated_at,
                inverse_rate=compute_inverse_rate(value),
            )
            observations.append(
                NormalizedFxObservation(
                    source_slug="crdb_forex",
                    metric_slug=metric_slug,
                    value=value,
                    recorded_at=source_last_updated_at,
                    external_reference=build_external_reference(
                        instrument_code=instrument_code,
                        metric_slug=metric_slug,
                        channel=detail.channel,
                        cash_note_band=None,
                        source_effective_date=source_effective_date,
                    ),
                    detail=detail,
                    location_path="TZ",
                    extra_data={
                        "source_page_url": source_url,
                        "raw_currency_name": instrument_name,
                        "row_number": row_index,
                        "raw_last_updated": raw_last_updated,
                    },
                    ingestion_metadata={
                        "content_sha256": content_sha256,
                        "parser": "crdb_forex_html_v1",
                    },
                )
            )
    return observations


def infer_crdb_run_status(observations: list[NormalizedFxObservation]) -> str:
    return "succeeded" if observations else "partial"


def extract_latest_crdb_timestamp(
    observations: list[NormalizedFxObservation],
) -> str | None:
    if not observations:
        return None
    latest = max(observation.recorded_at for observation in observations)
    return latest.isoformat()
