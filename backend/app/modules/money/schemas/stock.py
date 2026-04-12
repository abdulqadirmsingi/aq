"""Pydantic response schemas for DSE stock market data."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, model_validator


def _fmt_price(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return f"{round(float(value)):,}"


def _fmt_turnover(value: Decimal | None) -> str:
    if not value or value == 0:
        return "—"
    v = float(value)
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:.2f}B TZS"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M TZS"
    return f"{round(v):,} TZS"


def _fmt_change(value: Decimal | None) -> tuple[str, str]:
    """Returns (formatted_string, direction)."""
    if value is None:
        return "—", "unchanged"
    v = float(value)
    if v > 0:
        return f"+{v:.2f}%", "up"
    if v < 0:
        return f"{v:.2f}%", "down"
    return f"{v:.2f}%", "unchanged"


class DseStockRead(BaseModel):
    symbol: str
    exchange_code: str
    trade_date: date

    # Raw numeric values (float — serializes correctly as JSON numbers)
    close_price: float
    open_price: float | None
    high_price: float | None
    low_price: float | None
    change_pct: float | None
    turnover_tzs: float | None

    # Backend-formatted display strings — frontend renders these directly
    close_price_display: str = ""
    open_price_display: str = ""
    high_price_display: str = ""
    low_price_display: str = ""
    change_pct_display: str = ""
    change_direction: str = "unchanged"  # "up" | "down" | "unchanged"
    turnover_display: str = ""

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def _compute_display(self) -> "DseStockRead":
        self.close_price_display = _fmt_price(Decimal(str(self.close_price)))
        self.open_price_display = _fmt_price(
            Decimal(str(self.open_price)) if self.open_price is not None else None
        )
        self.high_price_display = _fmt_price(
            Decimal(str(self.high_price)) if self.high_price is not None else None
        )
        self.low_price_display = _fmt_price(
            Decimal(str(self.low_price)) if self.low_price is not None else None
        )
        change_pct_d = Decimal(str(self.change_pct)) if self.change_pct is not None else None
        self.change_pct_display, self.change_direction = _fmt_change(change_pct_d)
        self.turnover_display = _fmt_turnover(
            Decimal(str(self.turnover_tzs)) if self.turnover_tzs is not None else None
        )
        return self


class DseDashboardSummaryRead(BaseModel):
    trade_date: date | None
    total_symbols: int
    total_turnover: float
    total_turnover_display: str  # e.g. "3.5B TZS"
    top_gainer: DseStockRead | None
    top_loser: DseStockRead | None
    most_traded: DseStockRead | None
    gainers_count: int
    losers_count: int
    unchanged_count: int
