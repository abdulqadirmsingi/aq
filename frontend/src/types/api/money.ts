import type { ApiPage } from "./common";

export interface BotExchangeRateRead {
  snapshot_date: string;
  snapshot_month_label: string;
  instrument_code: string;
  instrument_name: string;
  quote_code: string;
  buy_rate: number | null;
  sell_rate: number | null;
  mean_rate: number | null;
  source_effective_date: string | null;
  source_last_updated_at: string | null;
  market_scope: string;
  created_at: string;
}

export interface BotExchangeRateAvailableMonthRead {
  month_start: string;
  month_label: string | null;
  observation_count: number;
}

export interface BotExchangeRateFiltersRead {
  instrument_codes: string[];
  latest_snapshot_date: string | null;
  latest_snapshot_month_label: string | null;
  available_months: BotExchangeRateAvailableMonthRead[];
}

export interface ExchangeRateComparisonRead {
  source_slug: string;
  source_name: string;
  snapshot_date: string;
  snapshot_month_label: string;
  instrument_code: string;
  instrument_name: string;
  quote_code: string;
  buy_rate: number | null;
  sell_rate: number | null;
  mean_rate: number | null;
  source_effective_date: string | null;
  source_last_updated_at: string | null;
  market_scope: string;
  channel: string | null;
  cash_note_band: string | null;
  created_at: string;
}

export interface ExchangeRateLatestComparisonRead {
  instrument_code: string;
  channel: string | null;
  cash_note_band: string | null;
  items: ExchangeRateComparisonRead[];
}

export interface ExchangeRateRecommendationCandidateRead {
  source_slug: string;
  source_name: string;
  snapshot_date: string;
  snapshot_month_label: string;
  instrument_code: string;
  instrument_name: string;
  quote_code: string;
  customer_action: string;
  relevant_rate: number;
  rate_label: string;
  buy_rate: number | null;
  sell_rate: number | null;
  mean_rate: number | null;
  source_effective_date: string | null;
  source_last_updated_at: string | null;
  market_scope: string;
  channel: string | null;
  cash_note_band: string | null;
  created_at: string;
  rank: number;
  difference_from_best: number | null;
  difference_from_bot_mean: number | null;
}

export interface ExchangeRateRecommendationRead {
  instrument_code: string;
  customer_action: string;
  channel: string | null;
  cash_note_band: string | null;
  best_option: ExchangeRateRecommendationCandidateRead | null;
  benchmark: ExchangeRateComparisonRead | null;
  compared_options: ExchangeRateRecommendationCandidateRead[];
}

export interface ExchangeRateSpreadRead {
  source_slug: string;
  source_name: string;
  snapshot_date: string;
  snapshot_month_label: string;
  instrument_code: string;
  instrument_name: string;
  buy_rate: number;
  sell_rate: number;
  spread: number;
  spread_percent_of_buy: number | null;
  market_scope: string;
  channel: string | null;
  cash_note_band: string | null;
  source_last_updated_at: string | null;
}

export interface ExchangeRateSpreadSummaryRead {
  instrument_code: string;
  channel: string | null;
  cash_note_band: string | null;
  items: ExchangeRateSpreadRead[];
}

export interface ExchangeRateBenchmarkGapRead {
  source_slug: string;
  source_name: string;
  snapshot_date: string;
  snapshot_month_label: string;
  instrument_code: string;
  instrument_name: string;
  comparison_basis: string;
  relevant_rate: number;
  bot_mean_rate: number;
  absolute_gap: number;
  percent_gap: number | null;
  market_scope: string;
  channel: string | null;
  cash_note_band: string | null;
}

export interface ExchangeRateBenchmarkGapSummaryRead {
  instrument_code: string;
  customer_action: string;
  channel: string | null;
  cash_note_band: string | null;
  bot_mean_rate: number | null;
  items: ExchangeRateBenchmarkGapRead[];
}

export interface ExchangeRateStalenessRead {
  source_slug: string;
  source_name: string;
  instrument_code: string;
  snapshot_date: string;
  source_effective_date: string | null;
  source_last_updated_at: string | null;
  data_timestamp: string;
  lag_hours_vs_freshest: number;
  is_freshest: boolean;
  market_scope: string;
  channel: string | null;
  cash_note_band: string | null;
}

export interface ExchangeRateStalenessSummaryRead {
  instrument_code: string;
  channel: string | null;
  cash_note_band: string | null;
  freshest_timestamp: string | null;
  items: ExchangeRateStalenessRead[];
}

export interface ExchangeRateBestRateRead {
  customer_action: string;
  best_option: ExchangeRateRecommendationCandidateRead | null;
  benchmark: ExchangeRateComparisonRead | null;
}

export interface ExchangeRateBestRateSummaryRead {
  instrument_code: string;
  channel: string | null;
  cash_note_band: string | null;
  buy_forex: ExchangeRateBestRateRead;
  sell_forex: ExchangeRateBestRateRead;
}

export interface ExchangeRateOpportunityRead {
  customer_action: string;
  best_source_slug: string;
  best_source_name: string;
  compared_source_slug: string;
  compared_source_name: string;
  instrument_code: string;
  relevant_rate: number;
  best_rate: number;
  absolute_difference: number;
  percent_difference: number | null;
  channel: string | null;
  cash_note_band: string | null;
}

export interface ExchangeRateOpportunitySummaryRead {
  instrument_code: string;
  customer_action: string;
  channel: string | null;
  cash_note_band: string | null;
  best_source_slug: string | null;
  opportunities: ExchangeRateOpportunityRead[];
}

export type BotExchangeRatePage = ApiPage<BotExchangeRateRead>;
