"""Parser for the iTrust Finance DSE market-summary API response."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime, time
from decimal import Decimal, InvalidOperation

from src.domains.money.stock_models import (
    NormalizedStockObservation,
    StockPriceDetailPayload,
)

_SOURCE_SLUG = "itrust_dse"
_METRIC_SLUG = "dse_close_price"
_EXCHANGE_CODE = "DSE"

SUMMARY_URL = "https://api.itrust.co.tz/api/market/summary"


def _to_decimal(value: object) -> Decimal | None:
    """Coerce a JSON number (int/float) to Decimal; returns None for 0 or missing."""
    if value is None:
        return None
    try:
        d = Decimal(str(value))
    except InvalidOperation:
        return None
    return d


def _trade_date(raw: str) -> date:
    """Parse the tradeDate string returned by the API (YYYY-MM-DD)."""
    return date.fromisoformat(raw)


def _recorded_at(trade_date: date) -> datetime:
    """Midnight UTC of the trade date — canonical recorded_at for the platform."""
    return datetime.combine(trade_date, time(0, 0, tzinfo=UTC))


def _external_reference(symbol: str, trade_date: date) -> str:
    return f"{symbol.upper()}|{trade_date.isoformat()}"


def parse_itrust_market_summary(
    raw_json: str,
    *,
    source_url: str = SUMMARY_URL,
) -> list[NormalizedStockObservation]:
    """Parse the `/api/market/summary` JSON text into normalized observations.

    Each row becomes one ``NormalizedStockObservation`` whose primary value is
    the close price.  Rows where Close == 0 are skipped (no valid close price).
    """
    content_sha256 = hashlib.sha256(raw_json.encode()).hexdigest()
    data = json.loads(raw_json)

    trade_date = _trade_date(data["tradeDate"])
    recorded_at = _recorded_at(trade_date)

    observations: list[NormalizedStockObservation] = []

    for row in data.get("data", []):
        symbol: str = row["Symbol"]
        close = _to_decimal(row.get("Close"))

        if close is None or close == 0:
            # No valid close price — skip (e.g. suspended stocks)
            continue

        open_price = _to_decimal(row.get("Open")) or None
        high_price = _to_decimal(row.get("High")) or None
        low_price = _to_decimal(row.get("Low")) or None
        change_pct = _to_decimal(row.get("Change"))  # can legitimately be 0
        turnover = _to_decimal(row.get("Turnover")) or None

        detail = StockPriceDetailPayload(
            symbol=symbol,
            trade_date=trade_date,
            exchange_code=_EXCHANGE_CODE,
            open_price=open_price,
            high_price=high_price if high_price and high_price > 0 else None,
            low_price=low_price if low_price and low_price > 0 else None,
            change_pct=change_pct,
            turnover_tzs=turnover,
        )

        obs = NormalizedStockObservation(
            source_slug=_SOURCE_SLUG,
            metric_slug=_METRIC_SLUG,
            value=close,
            recorded_at=recorded_at,
            external_reference=_external_reference(symbol, trade_date),
            detail=detail,
            ingestion_metadata={
                "content_sha256": content_sha256,
                "source_url": source_url,
            },
        )
        observations.append(obs)

    return observations
