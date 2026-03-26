from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ExchangeRateSourceDefinition:
    slug: str
    name: str
    source_type: str
    description: str
    url: str
    reliability_score: Decimal


@dataclass(frozen=True)
class ExchangeRateMetricDefinition:
    slug: str
    name: str
    description: str


MONEY_CATEGORY_SLUG = "money"
MONEY_CATEGORY_NAME = "Money"
MONEY_CATEGORY_DESCRIPTION = (
    "Exchange rates, inflation, and financial market observations."
)
TANZANIA_LOCATION_PATH = "TZ"

EXCHANGE_RATE_SOURCES: tuple[ExchangeRateSourceDefinition, ...] = (
    ExchangeRateSourceDefinition(
        slug="bot_exchange_rates",
        name="Bank of Tanzania Exchange Rates",
        source_type="government",
        description="Official Bank of Tanzania exchange-rate reference tables.",
        url="https://www.bot.go.tz/exchangerate/excrates",
        reliability_score=Decimal("0.980"),
    ),
    ExchangeRateSourceDefinition(
        slug="crdb_forex",
        name="CRDB Forex Rates",
        source_type="private",
        description="CRDB Bank foreign-exchange buy and sell rates.",
        url="https://crdbbank.co.tz/en/forex",
        reliability_score=Decimal("0.900"),
    ),
    ExchangeRateSourceDefinition(
        slug="nmb_daily_exchange_rates",
        name="NMB Daily Exchange Rates",
        source_type="private",
        description="NMB Bank daily non-cash and cash foreign-exchange rates.",
        url="https://www.nmbbank.co.tz/treasury/foreign-exchange/nmb-daily-exchange-rates",
        reliability_score=Decimal("0.900"),
    ),
)

EXCHANGE_RATE_METRICS: tuple[ExchangeRateMetricDefinition, ...] = (
    ExchangeRateMetricDefinition(
        slug="fx_buy_rate",
        name="FX Buy Rate",
        description="Observed source buying rate quoted against TZS.",
    ),
    ExchangeRateMetricDefinition(
        slug="fx_sell_rate",
        name="FX Sell Rate",
        description="Observed source selling rate quoted against TZS.",
    ),
    ExchangeRateMetricDefinition(
        slug="fx_mean_rate",
        name="FX Mean Rate",
        description="Observed source midpoint or mean rate quoted against TZS.",
    ),
)
