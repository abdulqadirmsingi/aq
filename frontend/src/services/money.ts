import { API_ENDPOINTS, MONEY_DEFAULTS } from "@/lib/constants";
import type {
  BotExchangeRateFiltersRead,
  BotExchangeRatePage,
  ExchangeRateBenchmarkGapSummaryRead,
  ExchangeRateBestRateSummaryRead,
  ExchangeRateLatestComparisonRead,
  ExchangeRateOpportunitySummaryRead,
  ExchangeRateRecommendationRead,
  ExchangeRateSpreadSummaryRead,
  ExchangeRateStalenessSummaryRead,
  MoneyDashboardSummaryRead,
} from "@/types/api";
import type { MoneyPageData, MoneyQueryState } from "@/features/money/types";
import { apiFetch } from "./api-client";

interface MoneyRateOptions {
  instrumentCode: string;
  channel?: string;
  cashNoteBand?: string;
}

interface MoneyActionOptions extends MoneyRateOptions {
  customerAction: "buy" | "sell";
}

interface BotHistoryOptions {
  instrumentCode: string;
  limit?: number;
  offset?: number;
}

function emptyBotFilters(): BotExchangeRateFiltersRead {
  return {
    instrument_codes: [],
    latest_snapshot_date: null,
    latest_snapshot_month_label: null,
    available_months: [],
  };
}

function emptyBotHistory(limit = MONEY_DEFAULTS.historyLimit): BotExchangeRatePage {
  return {
    items: [],
    meta: {
      limit,
      offset: 0,
      total: 0,
      has_next: false,
    },
  };
}

function emptyComparison(instrumentCode: string): ExchangeRateLatestComparisonRead {
  return {
    instrument_code: instrumentCode,
    channel: null,
    cash_note_band: null,
    items: [],
  };
}

function emptyRecommendation(
  instrumentCode: string,
  customerAction: "buy" | "sell",
): ExchangeRateRecommendationRead {
  return {
    instrument_code: instrumentCode,
    customer_action: customerAction,
    channel: null,
    cash_note_band: null,
    best_option: null,
    benchmark: null,
    compared_options: [],
  };
}

function emptySpreads(instrumentCode: string): ExchangeRateSpreadSummaryRead {
  return {
    instrument_code: instrumentCode,
    channel: null,
    cash_note_band: null,
    items: [],
  };
}

function emptyBenchmarkGaps(
  instrumentCode: string,
  customerAction: "buy" | "sell",
): ExchangeRateBenchmarkGapSummaryRead {
  return {
    instrument_code: instrumentCode,
    customer_action: customerAction,
    channel: null,
    cash_note_band: null,
    bot_mean_rate: null,
    items: [],
  };
}

function emptyStaleness(instrumentCode: string): ExchangeRateStalenessSummaryRead {
  return {
    instrument_code: instrumentCode,
    channel: null,
    cash_note_band: null,
    freshest_timestamp: null,
    items: [],
  };
}

function emptyBestRates(instrumentCode: string): ExchangeRateBestRateSummaryRead {
  return {
    instrument_code: instrumentCode,
    channel: null,
    cash_note_band: null,
    buy_forex: {
      customer_action: "buy",
      best_option: null,
      benchmark: null,
    },
    sell_forex: {
      customer_action: "sell",
      best_option: null,
      benchmark: null,
    },
  };
}

function emptyOpportunities(
  instrumentCode: string,
  customerAction: "buy" | "sell",
): ExchangeRateOpportunitySummaryRead {
  return {
    instrument_code: instrumentCode,
    customer_action: customerAction,
    channel: null,
    cash_note_band: null,
    best_source_slug: null,
    opportunities: [],
  };
}

async function safeRequest<T>(loader: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await loader();
  } catch {
    return fallback;
  }
}

export async function getMoneyBotFilters(): Promise<BotExchangeRateFiltersRead> {
  return apiFetch<BotExchangeRateFiltersRead>(API_ENDPOINTS.money.exchangeRates.botFilters);
}

export async function getMoneyDashboardSummary(
  instrumentCode = MONEY_DEFAULTS.defaultInstrumentCode,
): Promise<MoneyDashboardSummaryRead> {
  return apiFetch<MoneyDashboardSummaryRead>(
    API_ENDPOINTS.money.exchangeRates.dashboardSummary,
    {
      query: {
        instrument_code: instrumentCode,
      },
    },
  );
}

export async function getMoneyBotHistory(
  options: BotHistoryOptions,
): Promise<BotExchangeRatePage> {
  return apiFetch<BotExchangeRatePage>(API_ENDPOINTS.money.exchangeRates.botHistory, {
    query: {
      instrument_code: options.instrumentCode,
      limit: options.limit ?? MONEY_DEFAULTS.historyLimit,
      offset: options.offset ?? 0,
    },
  });
}

export async function getMoneyLatestComparison(
  options: MoneyRateOptions,
): Promise<ExchangeRateLatestComparisonRead> {
  return apiFetch<ExchangeRateLatestComparisonRead>(
    API_ENDPOINTS.money.exchangeRates.latestComparison,
    {
      query: {
        instrument_code: options.instrumentCode,
        channel: options.channel,
        cash_note_band: options.cashNoteBand,
      },
    },
  );
}

export async function getMoneyRecommendation(
  options: MoneyActionOptions,
): Promise<ExchangeRateRecommendationRead> {
  return apiFetch<ExchangeRateRecommendationRead>(
    API_ENDPOINTS.money.exchangeRates.recommendation,
    {
      query: {
        instrument_code: options.instrumentCode,
        customer_action: options.customerAction,
        channel: options.channel,
        cash_note_band: options.cashNoteBand,
      },
    },
  );
}

export async function getMoneySpreads(
  options: MoneyRateOptions,
): Promise<ExchangeRateSpreadSummaryRead> {
  return apiFetch<ExchangeRateSpreadSummaryRead>(API_ENDPOINTS.money.exchangeRates.spreads, {
    query: {
      instrument_code: options.instrumentCode,
      channel: options.channel,
      cash_note_band: options.cashNoteBand,
    },
  });
}

export async function getMoneyBenchmarkGaps(
  options: MoneyActionOptions,
): Promise<ExchangeRateBenchmarkGapSummaryRead> {
  return apiFetch<ExchangeRateBenchmarkGapSummaryRead>(
    API_ENDPOINTS.money.exchangeRates.benchmarkGaps,
    {
      query: {
        instrument_code: options.instrumentCode,
        customer_action: options.customerAction,
        channel: options.channel,
        cash_note_band: options.cashNoteBand,
      },
    },
  );
}

export async function getMoneyStaleness(
  options: MoneyRateOptions,
): Promise<ExchangeRateStalenessSummaryRead> {
  return apiFetch<ExchangeRateStalenessSummaryRead>(API_ENDPOINTS.money.exchangeRates.staleness, {
    query: {
      instrument_code: options.instrumentCode,
      channel: options.channel,
      cash_note_band: options.cashNoteBand,
    },
  });
}

export async function getMoneyBestRates(
  options: MoneyRateOptions,
): Promise<ExchangeRateBestRateSummaryRead> {
  return apiFetch<ExchangeRateBestRateSummaryRead>(API_ENDPOINTS.money.exchangeRates.bestRates, {
    query: {
      instrument_code: options.instrumentCode,
      channel: options.channel,
      cash_note_band: options.cashNoteBand,
    },
  });
}

export async function getMoneyOpportunities(
  options: MoneyActionOptions,
): Promise<ExchangeRateOpportunitySummaryRead> {
  return apiFetch<ExchangeRateOpportunitySummaryRead>(
    API_ENDPOINTS.money.exchangeRates.opportunities,
    {
      query: {
        instrument_code: options.instrumentCode,
        customer_action: options.customerAction,
        channel: options.channel,
        cash_note_band: options.cashNoteBand,
      },
    },
  );
}

export async function getMoneyPageData(query: MoneyQueryState): Promise<MoneyPageData> {
  const filters = await safeRequest(getMoneyBotFilters, emptyBotFilters());
  const instrumentCode = query.instrumentCode || filters.instrument_codes[0] || MONEY_DEFAULTS.defaultInstrumentCode;

  const options = {
    instrumentCode,
    channel: query.channel,
    cashNoteBand: query.cashNoteBand,
  };

  const [
    comparison,
    recommendation,
    spreads,
    benchmarkGaps,
    staleness,
    bestRates,
    opportunities,
    botHistory,
  ] = await Promise.all([
    safeRequest(() => getMoneyLatestComparison(options), emptyComparison(instrumentCode)),
    safeRequest(
      () =>
        getMoneyRecommendation({
          ...options,
          customerAction: query.customerAction,
        }),
      emptyRecommendation(instrumentCode, query.customerAction),
    ),
    safeRequest(() => getMoneySpreads(options), emptySpreads(instrumentCode)),
    safeRequest(
      () =>
        getMoneyBenchmarkGaps({
          ...options,
          customerAction: query.customerAction,
        }),
      emptyBenchmarkGaps(instrumentCode, query.customerAction),
    ),
    safeRequest(() => getMoneyStaleness(options), emptyStaleness(instrumentCode)),
    safeRequest(() => getMoneyBestRates(options), emptyBestRates(instrumentCode)),
    safeRequest(
      () =>
        getMoneyOpportunities({
          ...options,
          customerAction: query.customerAction,
        }),
      emptyOpportunities(instrumentCode, query.customerAction),
    ),
    safeRequest(
      () =>
        getMoneyBotHistory({
          instrumentCode,
          limit: MONEY_DEFAULTS.historyLimit,
          offset: query.historyOffset,
        }),
      emptyBotHistory(),
    ),
  ]);

  return {
    filters,
    query: {
      ...query,
      instrumentCode,
    },
    comparison,
    recommendation,
    spreads,
    benchmarkGaps,
    staleness,
    bestRates,
    opportunities,
    botHistory,
  };
}
