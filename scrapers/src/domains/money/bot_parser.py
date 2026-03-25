"""BOT exchange-rate table parser."""

from __future__ import annotations

from datetime import UTC, datetime
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
)

_BOT_METRIC_SLUGS: dict[str, str] = {
    "buy": "fx_buy_rate",
    "sell": "fx_sell_rate",
    "mean": "fx_mean_rate",
}


def parse_bot_exchange_rates_html(
    html: str,
    *,
    source_url: str,
) -> list[NormalizedFxObservation]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table#table1")
    if table is None:
        raise ValueError("BOT exchange-rate table not found.")

    observations: list[NormalizedFxObservation] = []
    content_sha256 = sha256(html.encode("utf-8")).hexdigest()
    for row_index, row in enumerate(table.select("tbody tr"), start=1):
        cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
        if len(cells) < 6:
            continue

        instrument_code = cells[1].upper()
        source_effective_date = datetime.strptime(cells[5], "%d-%b-%y").date()
        recorded_at = datetime(
            source_effective_date.year,
            source_effective_date.month,
            source_effective_date.day,
            tzinfo=UTC,
        )
        instrument_type = "commodity" if instrument_code == "GOLD" else "currency"

        for rate_kind, value in (
            ("buy", parse_decimal_number(cells[2])),
            ("sell", parse_decimal_number(cells[3])),
            ("mean", parse_decimal_number(cells[4])),
        ):
            metric_slug = _BOT_METRIC_SLUGS[rate_kind]
            detail = ExchangeRateDetailPayload(
                instrument_code=instrument_code,
                instrument_name=instrument_code,
                instrument_type=instrument_type,
                quote_code="TZS",
                rate_kind=rate_kind,
                market_scope="official_reference",
                source_effective_date=source_effective_date,
                inverse_rate=compute_inverse_rate(value),
            )
            observations.append(
                NormalizedFxObservation(
                    source_slug="bot_exchange_rates",
                    metric_slug=metric_slug,
                    value=value,
                    recorded_at=recorded_at,
                    external_reference=build_external_reference(
                        instrument_code=instrument_code,
                        metric_slug=metric_slug,
                        channel=None,
                        cash_note_band=None,
                        source_effective_date=source_effective_date,
                    ),
                    detail=detail,
                    location_path="TZ",
                    extra_data={
                        "source_page_url": source_url,
                        "raw_currency_code": instrument_code,
                        "row_number": row_index,
                        "transaction_date": source_effective_date.isoformat(),
                    },
                    ingestion_metadata={
                        "content_sha256": content_sha256,
                        "parser": "bot_exchange_rates_html_v1",
                    },
                )
            )
    return observations


def infer_bot_run_status(observations: list[NormalizedFxObservation]) -> str:
    return "succeeded" if observations else "partial"


def extract_latest_effective_date(
    observations: list[NormalizedFxObservation],
) -> str | None:
    if not observations:
        return None
    dates = [
        observation.detail.source_effective_date
        for observation in observations
        if observation.detail.source_effective_date is not None
    ]
    if not dates:
        return None
    latest = max(dates)
    return latest.isoformat() if latest is not None else None
