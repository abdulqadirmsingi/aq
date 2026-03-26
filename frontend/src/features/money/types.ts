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
} from "@/types/api";

export type MoneyCustomerAction = "buy" | "sell";
export type MoneyChannel = "counter" | "non_cash" | "cash";
export type MoneyCashNoteBand = "notes_50_500" | "notes_1_20";

export interface MoneyQueryState {
  instrumentCode: string;
  customerAction: MoneyCustomerAction;
  channel?: MoneyChannel;
  cashNoteBand?: MoneyCashNoteBand;
  historyOffset: number;
}

export interface MoneyPageData {
  filters: BotExchangeRateFiltersRead;
  query: MoneyQueryState;
  comparison: ExchangeRateLatestComparisonRead;
  recommendation: ExchangeRateRecommendationRead;
  spreads: ExchangeRateSpreadSummaryRead;
  benchmarkGaps: ExchangeRateBenchmarkGapSummaryRead;
  staleness: ExchangeRateStalenessSummaryRead;
  bestRates: ExchangeRateBestRateSummaryRead;
  opportunities: ExchangeRateOpportunitySummaryRead;
  botHistory: BotExchangeRatePage;
}
