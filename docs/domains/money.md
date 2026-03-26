# Money Domain

## Scope

This domain currently covers exchange rates, inflation, and stock market data.
The next implementation phase should focus on foreign-exchange rates from:

- Bank of Tanzania (BOT)
- CRDB Bank
- NMB Bank

The implementation must reuse the shared `data_points` time-series model, remain
fully isolated inside the `money/` module, and must not change the working fuel
implementation.

## Current State

- `data_points` is already partitioned monthly on `recorded_at`, which is a good
  fit for exchange-rate history.
- `exchange_rate_details` exists but is still too narrow for the real source
  shapes we need to support.
- Money exchange-rate repository, service, router, and scraper files are
  currently placeholders.
- Frontend money exchange-rate data is still mocked.

## Source Analysis

The observations below were taken from the public source pages on 2026-03-25.

### 1. BOT

Source: `https://www.bot.go.tz/exchangerate/excrates`

Observed structure:

- Table rendered in HTML and paginated on the page.
- Columns:
  - serial number
  - currency code
  - buying
  - selling
  - mean
  - transaction date
- Data is national-level and reference-oriented.
- The table contains more than standard bank currencies.
- Important edge case: BOT includes `GOLD`, so the current `String(3)` currency
  column is not sufficient.

Examples seen on 2026-03-25:

- `USD`: buy `2557.8218`, sell `2583.4`, mean `2570.6109`
- `EUR`: buy `2964.2597`, sell `2993.9023`, mean `2979.081`
- `GOLD`: buy `11690575.61`, sell `11807481.37`, mean `11749028.49`

### 2. CRDB

Source: `https://crdbbank.co.tz/en/forex`

Observed structure:

- The page has a date filter and a visible `Last Updated` timestamp.
- Main table columns:
  - currency name
  - code
  - buying
  - selling
- Rates appear to be retail/commercial bank rates.
- The page also powers a currency converter from the same dataset.

Examples seen on 2026-03-25:

- `Last Updated`: `Mar 25, 2026, 22:33`
- `USD`: buy `2535`, sell `2615`
- `EUR`: buy `2,846.88`, sell `3,146.88`

### 3. NMB

Source: `https://www.nmbbank.co.tz/treasury/foreign-exchange/nmb-daily-exchange-rates`

Observed structure:

- The page presents two distinct rate families:
  - non-cash rates
  - cash rates
- Non-cash columns:
  - currency
  - code
  - buy
  - sell
- Cash columns are split by denomination bucket:
  - `50 - 500 Buy`
  - `50 - 500 Sell`
  - `1 - 20 Buy`
  - `1 - 20 Sell`
- This means a single source/day/currency can produce up to 6 numeric facts.

Examples seen on 2026-03-25:

- Non-cash `USD`: buy `2,535`, sell `2,615`
- Cash `USD`:
  - `50-500` buy `2,535`, sell `2,615`
  - `1-20` buy `2,535`, sell `2,615`
- Non-cash `KES`: buy `17.2`, sell `21.8`

## Design Principles

### 1. Keep `data_points` as the canonical fact table

Every numeric exchange-rate observation should remain a `data_points` row:

- one row per numeric rate value
- `recorded_at` stores the effective observation timestamp
- `source_id` identifies BOT, CRDB, or NMB
- `metric_id` identifies whether the value is buy, sell, or mean
- `exchange_rate_details` stores the dimensions needed to interpret the value

This matches the fuel design pattern and preserves shared analytics capability.

### 2. Store exact observations, not only monthly summaries

We should store each daily or intraday snapshot exactly as published.

Why:

- recommendations need the latest available rate
- month-over-month analysis can be derived later
- re-runs must be idempotent
- audits need the original observed value and source timestamp

Monthly recording is already supported by the partitioning strategy because
`data_points` is partitioned by month on `recorded_at`.

### 3. Normalize without losing source-specific meaning

We should not flatten everything into a simple `USD/TZS buy/sell` model because:

- BOT has `mean`
- NMB has `cash` and `non_cash`
- NMB cash has denomination buckets
- future banks may introduce branch rates, ATM rates, card rates, or special
  channels

## Recommended Schema Changes

### Keep

- `data_categories`
- `sources`
- `metrics`
- `locations`
- `data_points`
- `exchange_rate_details`

### Modify `exchange_rate_details`

The current table:

- `base_currency`
- `quote_currency`
- `rate_type`
- `market`
- `inverse_rate`

is not enough for BOT, CRDB, and NMB.

Recommended replacement structure:

- `instrument_code VARCHAR(16) NOT NULL`
  - replaces `base_currency`
  - supports `USD`, `EUR`, `GOLD`, and future non-3-char instruments
- `instrument_name VARCHAR(120) NULL`
  - stores the source label, for example `US DOLLAR`
- `instrument_type VARCHAR(24) NOT NULL DEFAULT 'currency'`
  - values like `currency`, `commodity`, `special_unit`
- `quote_code VARCHAR(16) NOT NULL DEFAULT 'TZS'`
  - replaces `quote_currency`
- `rate_kind VARCHAR(24) NOT NULL`
  - values like `buy`, `sell`, `mean`
- `market_scope VARCHAR(32) NOT NULL`
  - values like `official_reference`, `commercial_bank`
- `channel VARCHAR(32) NULL`
  - values like `non_cash`, `cash`, `counter`
- `cash_note_band VARCHAR(32) NULL`
  - values like `notes_50_500`, `notes_1_20`
- `source_effective_date DATE NULL`
  - the date shown by the source, if available
- `source_last_updated_at TIMESTAMPTZ NULL`
  - visible update time such as CRDB `Last Updated`
- `inverse_rate NUMERIC(24, 8) NULL`
  - still useful for some downstream uses

Recommended indexes:

- `(instrument_code, quote_code, rate_kind, data_point_recorded_at desc)`
- `(market_scope, channel)`
- `(source_effective_date)`
- `(source_last_updated_at)`

### Metric Strategy

Use separate metrics for the semantic numeric facts:

- `fx_buy_rate`
- `fx_sell_rate`
- `fx_mean_rate`

Why this is better than one generic metric:

- makes downstream queries simpler
- keeps business meaning explicit
- avoids overloading `rate_kind` as the only differentiator
- works well with recommendation queries

### Source Records to Seed

Seed or upsert these sources if they do not already exist:

- `bot_exchange_rates`
- `crdb_forex`
- `nmb_daily_exchange_rates`

Suggested source types:

- BOT: `government`
- CRDB: `private`
- NMB: `private`

### Optional But Recommended

Create or reuse a Tanzania country location and attach national-level FX rates to
that `location_id` instead of leaving everything global/null. This helps later if
we add branch, region, or country-level filtering.

## What the Backend Should Expect

### Normalized Ingestion DTO

All scrapers should normalize to one internal DTO before persistence:

```python
@dataclass(frozen=True)
class NormalizedFxObservation:
    source_slug: str
    instrument_code: str
    instrument_name: str | None
    instrument_type: str
    quote_code: str
    metric_slug: str
    rate_kind: str
    value: Decimal
    market_scope: str
    channel: str | None
    cash_note_band: str | None
    location_code: str | None
    source_effective_date: date | None
    source_last_updated_at: datetime | None
    recorded_at: datetime
    external_reference: str
    extra_data: dict[str, Any]
    ingestion_metadata: dict[str, Any]
```

### `recorded_at` Rules

- If the source has a full timestamp, use it.
- If the source only has a date, record at Tanzania midnight or midday
  consistently.
- Use one shared helper so all sources resolve dates the same way.
- Keep the original raw date/time strings in `extra_data`.

Recommended rule:

- BOT: use `transaction_date` at Tanzania `00:00:00`
- NMB: if no visible time is provided, use Tanzania `00:00:00`
- CRDB: use the visible `Last Updated` timestamp when available

### `external_reference` Rules

This is critical because the `data_points` dedupe key includes
`external_reference`.

Recommended pattern:

```text
{instrument_code}|{metric_slug}|{channel or na}|{cash_note_band or na}|{source_effective_date}
```

Examples:

- `USD|fx_buy_rate|non_cash|na|2026-03-25`
- `USD|fx_sell_rate|cash|notes_50_500|2026-03-25`
- `GOLD|fx_mean_rate|na|na|2026-03-25`

This prevents collisions between:

- buy vs sell
- cash vs non-cash
- note buckets
- same-day multi-rate observations

## Persistence Logic

### Per Observation

For each normalized row:

1. Resolve `source_id`
2. Resolve `metric_id`
3. Resolve `location_id`
4. Insert or upsert `data_points`
5. Insert matching `exchange_rate_details`

### DataPoint Payload Guidance

- `value_numeric`: the rate value
- `unit_override`: `TZS`
- `value_type`: `numeric`
- `extra_data`:
  - raw currency name
  - raw published date string
  - raw updated-at string
  - source page url
  - parser version
  - channel labels from the source page
- `ingestion_metadata`:
  - fetch timestamp
  - response fingerprint/hash
  - scraper version
  - raw html checksum

### Idempotency

The scraper must be safe to rerun for the same source/date.

Rules:

- if the exact same observation is seen again, do not duplicate it
- if the same source/date/currency/rate-kind changes later in the day:
  - insert a new `data_points` row if the source timestamp changed
  - otherwise update via versioning only if the project later chooses a
    correction flow

For phase 1 and phase 2, prefer append-only snapshots when timestamps differ.

## Query and Recommendation Logic

### Core Query Scenarios

The backend should support these queries first:

1. latest rates by source
2. rate history for a source and currency
3. latest comparison across sources for one currency
4. monthly trend for one currency and rate kind
5. latest recommendation for buying or selling a currency

### Recommendation Rules

For a customer who wants to buy foreign currency:

- compare `sell` rates across eligible providers
- lower `sell` is better

For a customer who wants to sell foreign currency:

- compare `buy` rates across eligible providers
- higher `buy` is better

Filtering dimensions:

- instrument code
- as-of date/time
- eligible sources
- channel preference
- cash note band
- include/exclude BOT reference rates

Important:

- BOT should usually be treated as a reference benchmark, not automatically as a
  retail recommendation.
- Recommendation endpoints should return both the winner and the comparison set,
  so the frontend can explain the choice.

### Derived Analytics Worth Supporting

- best source to buy a given currency now
- best source to sell a given currency now
- gap between commercial bank rates and BOT reference
- bank spread by currency: `sell - buy`
- cheapest channel: cash vs non-cash
- monthly min/max/average by source and currency
- staleness detection when one provider has not updated recently
- anomaly detection when a bank deviates sharply from BOT or its own history

## Suggested API Shape

Phase 1 does not need every endpoint, but this is the target structure.

### Filters

`GET /api/v1/money/exchange-rates/filters`

Returns:

- sources
- supported instruments
- available channels
- available note bands
- available months
- latest snapshot per source

### Latest Source Comparison

`GET /api/v1/money/exchange-rates/latest`

Query params:

- `instrument_code`
- `metric` or `customer_action`
- `channel`
- `cash_note_band`
- `as_of`

### History

`GET /api/v1/money/exchange-rates/history`

Query params:

- `instrument_code`
- `source`
- `metric`
- `channel`
- `year`
- `month`
- `limit`
- `offset`

### Recommendation

`GET /api/v1/money/exchange-rates/recommendation`

Query params:

- `instrument_code`
- `customer_action=buy|sell`
- `channel`
- `cash_note_band`
- `as_of`

Response should include:

- selected winner
- compared rates
- benchmark rate from BOT when available
- spread and savings/difference calculations
- source timestamps so stale data is visible

## Phased Implementation Plan

### Phase 1: Schema and Catalog Foundation

Goal:

- make the data model capable of storing BOT, CRDB, and NMB safely

Tasks:

- expand/refactor `exchange_rate_details`
- create Alembic migration
- seed metrics: `fx_buy_rate`, `fx_sell_rate`, `fx_mean_rate`
- seed sources for BOT, CRDB, NMB
- add shared money-domain enums/constants
- add repository-level tests for schema assumptions

Exit criteria:

- a single normalized FX observation can be persisted end-to-end
- no fuel code or energy routes are modified

### Phase 2: Shared Money FX Ingestion Foundation

Goal:

- create reusable parsing and persistence building blocks

Tasks:

- add normalized DTOs
- add source-independent persistence service/repository helpers
- add shared timestamp parsing and numeric cleaning helpers
- add idempotent save flow into `data_points` + `exchange_rate_details`
- add scraper test fixtures with mocked HTML

Exit criteria:

- any source parser can emit normalized observations and persist them

### Phase 3: BOT Implementation

Goal:

- ingest official BOT reference rates first

Why BOT first:

- richest and most complete reference dataset
- includes `buy`, `sell`, and `mean`
- gives us the baseline benchmark for later bank comparisons

Tasks:

- implement BOT scraper/parser
- parse paginated HTML table correctly
- support non-standard instruments like `GOLD`
- persist BOT daily observations
- add latest/history endpoints for BOT-backed queries

Exit criteria:

- BOT rates are queryable historically by instrument and month

### Phase 4: CRDB Implementation

Goal:

- add commercial bank comparison data with source timestamps

Tasks:

- implement CRDB scraper/parser
- capture visible `Last Updated`
- support date-based fetching if the site allows it reliably
- persist buy/sell observations
- expose latest comparison including BOT + CRDB

Exit criteria:

- CRDB can be compared against BOT for supported currencies

### Phase 5: NMB Implementation

Goal:

- support richer bank channel logic

Tasks:

- implement NMB scraper/parser
- persist `non_cash`
- persist `cash`
- persist note-band splits for cash
- expose channel-aware comparison queries

Exit criteria:

- the API can distinguish non-cash vs cash recommendations

### Phase 6: Recommendation and Analytics Layer

Goal:

- answer “where should I go to buy or sell currency now?”

Tasks:

- add comparison service
- add recommendation endpoint
- add monthly rollup queries
- add source staleness logic
- add benchmark/gap calculations versus BOT

Exit criteria:

- the backend returns a ranked, explainable recommendation set

### Phase 7: Frontend and Operationalization

Goal:

- replace mock money FX data with live backend data

Tasks:

- wire frontend services to backend endpoints
- show source, timestamp, channel, and benchmark comparisons
- add scheduled scraper runs
- add alerting/logging for scraper failures and stale rates

Exit criteria:

- dashboard uses real exchange-rate data end-to-end

## Edge Cases To Handle Explicitly

- BOT instruments not limited to 3 characters
- commodity-like entries such as `GOLD`
- old or uncommon currency codes
- missing timestamps on bank pages
- rates published with commas and mixed decimal formatting
- same-day rate updates from the same bank
- source temporarily removing a currency
- channel-specific duplication, especially in NMB cash vs non-cash
- stale source data being incorrectly recommended as “best”
- future new banks with additional dimensions like branch or ATM channel

## Recommended Implementation Order

The safest order is:

1. schema changes
2. shared normalization/persistence helpers
3. BOT
4. CRDB
5. NMB
6. comparison and recommendation logic
7. frontend integration

This order delivers value early, keeps the design flexible, and avoids
overfitting the model to one bank page before the shared shape is stable.
