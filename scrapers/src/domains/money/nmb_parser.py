"""NMB daily exchange-rates parser."""

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

_METRIC_SLUGS: dict[str, str] = {
    "buy": "fx_buy_rate",
    "sell": "fx_sell_rate",
}
_NOTE_BANDS: tuple[tuple[str, str, int, int], ...] = (
    ("notes_50_500", "50 - 500", 2, 3),
    ("notes_1_20", "1 - 20", 4, 5),
)


def parse_nmb_daily_exchange_rates_html(
    html: str,
    *,
    source_url: str,
    observed_at: datetime | None = None,
) -> list[NormalizedFxObservation]:
    soup = BeautifulSoup(html, "lxml")
    headings = soup.find_all(["h1", "h2", "h3"])
    if not headings:
        raise ValueError("NMB exchange-rate headings not found.")

    timestamp = observed_at or datetime.now(UTC)
    source_effective_date = timestamp.date()
    content_sha256 = sha256(html.encode("utf-8")).hexdigest()
    observations: list[NormalizedFxObservation] = []
    for heading in headings:
        channel_label = heading.get_text(" ", strip=True).lower()
        if "non cash" not in channel_label and "cash" not in channel_label:
            continue

        table = heading.find_next("table")
        if table is None:
            continue
        if "non cash" in channel_label:
            observations.extend(
                _parse_non_cash_table(
                    table,
                    source_url=source_url,
                    source_effective_date=source_effective_date,
                    recorded_at=timestamp,
                    content_sha256=content_sha256,
                )
            )
        elif "cash" in channel_label:
            observations.extend(
                _parse_cash_table(
                    table,
                    source_url=source_url,
                    source_effective_date=source_effective_date,
                    recorded_at=timestamp,
                    content_sha256=content_sha256,
                )
            )
    if observations:
        return observations

    tables = soup.select("#exchange-rate table")
    if len(tables) >= 1:
        observations.extend(
            _parse_non_cash_table(
                tables[0],
                source_url=source_url,
                source_effective_date=source_effective_date,
                recorded_at=timestamp,
                content_sha256=content_sha256,
            )
        )
    if len(tables) >= 2:
        observations.extend(
            _parse_cash_table(
                tables[1],
                source_url=source_url,
                source_effective_date=source_effective_date,
                recorded_at=timestamp,
                content_sha256=content_sha256,
            )
        )
    return observations


def parse_nmb_daily_exchange_rates_markdown(
    markdown: str,
    *,
    source_url: str,
    observed_at: datetime | None = None,
) -> list[NormalizedFxObservation]:
    timestamp = observed_at or datetime.now(UTC)
    source_effective_date = timestamp.date()
    content_sha256 = sha256(markdown.encode("utf-8")).hexdigest()
    observations: list[NormalizedFxObservation] = []
    lines = [line.strip() for line in markdown.splitlines()]

    non_cash_rows = _extract_markdown_table_rows(
        lines,
        "FOREX MARKET: NON CASH EXCHANGE RATES",
    )
    for row_index, cells in enumerate(non_cash_rows, start=1):
        if len(cells) != 5:
            continue
        _, instrument_name, instrument_code, buy_raw, sell_raw = cells
        observations.extend(
            _build_non_cash_observations(
                instrument_name=instrument_name,
                instrument_code=instrument_code.upper(),
                buy_raw=buy_raw,
                sell_raw=sell_raw,
                source_url=source_url,
                source_effective_date=source_effective_date,
                recorded_at=timestamp,
                content_sha256=content_sha256,
                row_index=row_index,
                parser_name="nmb_daily_exchange_rates_markdown_v1",
            )
        )

    cash_rows = _extract_markdown_table_rows(
        lines,
        "FOREX MARKET: CASH EXCHANGE RATES",
    )
    for row_index, cells in enumerate(cash_rows, start=1):
        if len(cells) != 6:
            continue
        (
            instrument_name,
            instrument_code,
            buy_50_500,
            sell_50_500,
            buy_1_20,
            sell_1_20,
        ) = cells
        observations.extend(
            _build_cash_observations(
                instrument_name=instrument_name,
                instrument_code=instrument_code.upper(),
                buy_50_500=buy_50_500,
                sell_50_500=sell_50_500,
                buy_1_20=buy_1_20,
                sell_1_20=sell_1_20,
                source_url=source_url,
                source_effective_date=source_effective_date,
                recorded_at=timestamp,
                content_sha256=content_sha256,
                row_index=row_index,
                parser_name="nmb_daily_exchange_rates_markdown_v1",
            )
        )

    return observations


def _parse_non_cash_table(
    table,
    *,
    source_url: str,
    source_effective_date,
    recorded_at: datetime,
    content_sha256: str,
) -> list[NormalizedFxObservation]:
    observations: list[NormalizedFxObservation] = []
    for row_index, row in enumerate(table.select("tr"), start=1):
        cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
        if len(cells) < 4:
            continue
        if len(cells) >= 5:
            instrument_name = cells[1]
            instrument_code = cells[2].upper()
            buy_raw = cells[3]
            sell_raw = cells[4]
        else:
            instrument_name = cells[0]
            instrument_code = cells[1].upper()
            buy_raw = cells[2]
            sell_raw = cells[3]
        observations.extend(
            _build_non_cash_observations(
                instrument_name=instrument_name,
                instrument_code=instrument_code,
                buy_raw=buy_raw,
                sell_raw=sell_raw,
                source_url=source_url,
                source_effective_date=source_effective_date,
                recorded_at=recorded_at,
                content_sha256=content_sha256,
                row_index=row_index,
                parser_name="nmb_daily_exchange_rates_html_v1",
            )
        )
    return observations


def _parse_cash_table(
    table,
    *,
    source_url: str,
    source_effective_date,
    recorded_at: datetime,
    content_sha256: str,
) -> list[NormalizedFxObservation]:
    observations: list[NormalizedFxObservation] = []
    for row_index, row in enumerate(table.select("tr"), start=1):
        cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
        if len(cells) < 6:
            continue
        instrument_name = cells[0]
        instrument_code = cells[1].upper()
        observations.extend(
            _build_cash_observations(
                instrument_name=instrument_name,
                instrument_code=instrument_code,
                buy_50_500=cells[2],
                sell_50_500=cells[3],
                buy_1_20=cells[4],
                sell_1_20=cells[5],
                source_url=source_url,
                source_effective_date=source_effective_date,
                recorded_at=recorded_at,
                content_sha256=content_sha256,
                row_index=row_index,
                parser_name="nmb_daily_exchange_rates_html_v1",
            )
        )
    return observations


def infer_nmb_run_status(observations: list[NormalizedFxObservation]) -> str:
    return "succeeded" if observations else "partial"


def extract_latest_nmb_timestamp(
    observations: list[NormalizedFxObservation],
) -> str | None:
    if not observations:
        return None
    latest = max(observation.recorded_at for observation in observations)
    return latest.isoformat()


def _build_non_cash_observations(
    *,
    instrument_name: str,
    instrument_code: str,
    buy_raw: str,
    sell_raw: str,
    source_url: str,
    source_effective_date,
    recorded_at: datetime,
    content_sha256: str,
    row_index: int,
    parser_name: str,
) -> list[NormalizedFxObservation]:
    observations: list[NormalizedFxObservation] = []
    for rate_kind, value in (
        ("buy", parse_decimal_number(buy_raw)),
        ("sell", parse_decimal_number(sell_raw)),
    ):
        metric_slug = _METRIC_SLUGS[rate_kind]
        detail = ExchangeRateDetailPayload(
            instrument_code=instrument_code,
            instrument_name=instrument_name,
            quote_code="TZS",
            rate_kind=rate_kind,
            market_scope="commercial_bank",
            channel="non_cash",
            source_effective_date=source_effective_date,
            inverse_rate=compute_inverse_rate(value),
        )
        observations.append(
            NormalizedFxObservation(
                source_slug="nmb_daily_exchange_rates",
                metric_slug=metric_slug,
                value=value,
                recorded_at=recorded_at,
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
                    "section": "non_cash",
                },
                ingestion_metadata={
                    "content_sha256": content_sha256,
                    "parser": parser_name,
                },
            )
        )
    return observations


def _build_cash_observations(
    *,
    instrument_name: str,
    instrument_code: str,
    buy_50_500: str,
    sell_50_500: str,
    buy_1_20: str,
    sell_1_20: str,
    source_url: str,
    source_effective_date,
    recorded_at: datetime,
    content_sha256: str,
    row_index: int,
    parser_name: str,
) -> list[NormalizedFxObservation]:
    observations: list[NormalizedFxObservation] = []
    for note_band, label, buy_raw, sell_raw in (
        ("notes_50_500", "50 - 500", buy_50_500, sell_50_500),
        ("notes_1_20", "1 - 20", buy_1_20, sell_1_20),
    ):
        for rate_kind, value in (
            ("buy", parse_decimal_number(buy_raw)),
            ("sell", parse_decimal_number(sell_raw)),
        ):
            metric_slug = _METRIC_SLUGS[rate_kind]
            detail = ExchangeRateDetailPayload(
                instrument_code=instrument_code,
                instrument_name=instrument_name,
                quote_code="TZS",
                rate_kind=rate_kind,
                market_scope="commercial_bank",
                channel="cash",
                cash_note_band=note_band,
                source_effective_date=source_effective_date,
                inverse_rate=compute_inverse_rate(value),
            )
            observations.append(
                NormalizedFxObservation(
                    source_slug="nmb_daily_exchange_rates",
                    metric_slug=metric_slug,
                    value=value,
                    recorded_at=recorded_at,
                    external_reference=build_external_reference(
                        instrument_code=instrument_code,
                        metric_slug=metric_slug,
                        channel=detail.channel,
                        cash_note_band=note_band,
                        source_effective_date=source_effective_date,
                    ),
                    detail=detail,
                    location_path="TZ",
                    extra_data={
                        "source_page_url": source_url,
                        "raw_currency_name": instrument_name,
                        "row_number": row_index,
                        "section": "cash",
                        "note_band_label": label,
                    },
                    ingestion_metadata={
                        "content_sha256": content_sha256,
                        "parser": parser_name,
                    },
                )
            )
    return observations


def _extract_markdown_table_rows(
    lines: list[str],
    marker: str,
) -> list[list[str]]:
    try:
        start_index = lines.index(marker)
    except ValueError:
        return []

    rows: list[list[str]] = []
    seen_table = False
    for line in lines[start_index + 1 :]:
        if not line:
            if seen_table:
                break
            continue
        if not line.startswith("|"):
            if seen_table:
                break
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        seen_table = True
        if all(set(cell) <= {"-"} for cell in cells):
            continue
        if cells[0] in {"#", "Currency", ""}:
            continue
        rows.append(cells)
    return rows
