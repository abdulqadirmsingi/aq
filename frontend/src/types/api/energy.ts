import type { ApiPage } from "./common";

export interface EwuraFuelObservationRead {
  id: string;
  source_id: string;
  source_label: string;
  scraper_run_id: string | null;
  document_url: string;
  content_sha256: string;
  published_date: string | null;
  location_id: string | null;
  canonical_location_name: string | null;
  canonical_region_name: string | null;
  raw_location_text: string;
  fuel_type: string;
  price: number;
  price_display: string;
  unit: string;
  recorded_at: string;
  month_label: string;
  created_at: string;
}

export interface EwuraFuelLatestPriceRead {
  snapshot_date: string;
  snapshot_month_label: string;
  previous_snapshot_date: string | null;
  previous_snapshot_month_label: string | null;
  location_id: string | null;
  canonical_location_name: string | null;
  canonical_region_name: string | null;
  raw_location_text: string;
  fuel_type: string;
  price: number;
  price_display: string;
  previous_price: number | null;
  previous_price_display: string | null;
  absolute_change: number | null;
  absolute_change_display: string | null;
  percent_change: number | null;
  unit: string;
  document_url: string;
}

export interface EwuraFuelFiltersRead {
  fuel_types: string[];
  history_years: number[];
  latest_snapshot_date: string | null;
  latest_snapshot_month_label: string | null;
}

export interface EwuraFuelLatestSummaryItemRead {
  fuel_type: string;
  locations_count: number;
  avg_price: number;
  avg_price_display: string;
  min_price: number;
  min_price_display: string;
  max_price: number;
  max_price_display: string;
}

export interface EwuraFuelLatestSummaryRead {
  snapshot_date: string;
  snapshot_month_label: string;
  items: EwuraFuelLatestSummaryItemRead[];
}

export interface EwuraFuelMonthlyTrendRead {
  month_start: string;
  month_label: string;
  fuel_type: string;
  avg_price: number;
  avg_price_display: string;
  min_price: number;
  min_price_display: string;
  max_price: number;
  max_price_display: string;
  locations_count: number;
}

export interface EwuraFuelAvailableMonthRead {
  month_start: string;
  month_label: string;
  observation_count: number;
  locations_count: number;
}

export interface EwuraFuelRollupRead {
  snapshot_date: string;
  snapshot_month_label: string;
  level: string;
  group_name: string;
  fuel_type: string;
  observations_count: number;
  avg_price: number;
  avg_price_display: string;
  min_price: number;
  min_price_display: string;
  max_price: number;
  max_price_display: string;
}

export interface EwuraFuelExtremeItemRead {
  location_id: string | null;
  canonical_location_name: string | null;
  raw_location_text: string;
  fuel_type: string;
  price: number;
  price_display: string;
  document_url: string;
}

export interface EwuraFuelLatestExtremesRead {
  snapshot_date: string;
  snapshot_month_label: string;
  fuel_type: string | null;
  cheapest: EwuraFuelExtremeItemRead[];
  most_expensive: EwuraFuelExtremeItemRead[];
}

export interface EwuraFuelInsightRead {
  title: string;
  body: string;
  fuel_type: string | null;
}

export interface EwuraFuelDashboardSummaryRead {
  latest_summary: EwuraFuelLatestSummaryRead | null;
  latest_prices_preview: EwuraFuelLatestPriceRead[];
  current_year_trends: EwuraFuelMonthlyTrendRead[];
  available_months: EwuraFuelAvailableMonthRead[];
  insights: EwuraFuelInsightRead[];
}

export interface EwuraFuelRunRead {
  id: string;
  scraper_name: string;
  trigger_type: string;
  status: string;
  category_slug: string | null;
  source_name: string | null;
  started_at: string | null;
  finished_at: string | null;
  records_read: number;
  records_inserted: number;
  records_updated: number;
  records_rejected: number;
  error_message: string | null;
  run_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface EwuraFuelRunLogRead {
  id: string;
  scraper_run_id: string;
  data_point_id: string | null;
  data_point_recorded_at: string | null;
  level: string;
  event_type: string;
  message: string;
  details: Record<string, unknown>;
  created_at: string;
}

export type EwuraFuelObservationPage = ApiPage<EwuraFuelObservationRead>;
export type EwuraFuelLatestPricePage = ApiPage<EwuraFuelLatestPriceRead>;
export type EwuraFuelRunPage = ApiPage<EwuraFuelRunRead>;
export type EwuraFuelRunLogPage = ApiPage<EwuraFuelRunLogRead>;
