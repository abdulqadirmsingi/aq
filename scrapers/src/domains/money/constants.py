from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ExchangeRateSourceSeed:
    slug: str
    name: str
    source_type: str
    description: str
    url: str
    reliability_score: Decimal


@dataclass(frozen=True)
class ExchangeRateMetricSeed:
    slug: str
    name: str
    description: str


MONEY_CATEGORY_SLUG = "money"
MONEY_CATEGORY_NAME = "Money"
MONEY_CATEGORY_DESCRIPTION = (
    "Exchange rates, inflation, and financial market observations."
)
TANZANIA_LOCATION_PATH = "TZ"
TANZANIA_COUNTRY_NAME = "Tanzania"
TANZANIA_COUNTRY_CODE = "TZ"
TANZANIA_COUNTRY_CODE_ALPHA3 = "TZA"

EXCHANGE_RATE_SOURCES: tuple[ExchangeRateSourceSeed, ...] = (
    ExchangeRateSourceSeed(
        slug="bot_exchange_rates",
        name="Bank of Tanzania Exchange Rates",
        source_type="government",
        description="Official Bank of Tanzania exchange-rate reference tables.",
        url="https://www.bot.go.tz/exchangerate/excrates",
        reliability_score=Decimal("0.980"),
    ),
    ExchangeRateSourceSeed(
        slug="crdb_forex",
        name="CRDB Forex Rates",
        source_type="private",
        description="CRDB Bank foreign-exchange buy and sell rates.",
        url="https://crdbbank.co.tz/en/forex",
        reliability_score=Decimal("0.900"),
    ),
    ExchangeRateSourceSeed(
        slug="nmb_daily_exchange_rates",
        name="NMB Daily Exchange Rates",
        source_type="private",
        description="NMB Bank daily non-cash and cash foreign-exchange rates.",
        url="https://www.nmbbank.co.tz/treasury/foreign-exchange/nmb-daily-exchange-rates",
        reliability_score=Decimal("0.900"),
    ),
)

ITRUST_DSE_SOURCE = ExchangeRateSourceSeed(
    slug="itrust_dse",
    name="iTrust DSE Market Summary",
    source_type="private",
    description="Daily DSE stock OHLCV data aggregated and published by iTrust Finance.",
    url="https://itrust.co.tz/today-market",
    reliability_score=Decimal("0.880"),
)

STOCK_METRIC_SLUG = "dse_close_price"

EXCHANGE_RATE_METRICS: tuple[ExchangeRateMetricSeed, ...] = (
    ExchangeRateMetricSeed(
        slug="fx_buy_rate",
        name="FX Buy Rate",
        description="Observed source buying rate quoted against TZS.",
    ),
    ExchangeRateMetricSeed(
        slug="fx_sell_rate",
        name="FX Sell Rate",
        description="Observed source selling rate quoted against TZS.",
    ),
    ExchangeRateMetricSeed(
        slug="fx_mean_rate",
        name="FX Mean Rate",
        description="Observed source midpoint or mean rate quoted against TZS.",
    ),
)
