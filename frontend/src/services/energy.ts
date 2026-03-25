import { ENERGY_DEFAULTS, API_ENDPOINTS } from "@/lib/constants";
import type {
  EwuraFuelAvailableMonthRead,
  EwuraFuelDashboardSummaryRead,
  EwuraFuelFiltersRead,
  EwuraFuelInsightRead,
  EwuraFuelLatestExtremesRead,
  EwuraFuelLatestPricePage,
  EwuraFuelMonthlyTrendRead,
  EwuraFuelObservationPage,
  EwuraFuelRollupRead,
} from "@/types/api";
import type { EnergyPageData, EnergyQueryState } from "@/features/energy/types";
import { apiFetch } from "./api-client";

interface HistoryOptions {
  marketSegment?: "retail" | "wholesale";
  year?: number;
  fuelType?: string;
  locationQuery?: string;
  limit?: number;
  offset?: number;
}

interface LatestPricesOptions {
  marketSegment?: "retail" | "wholesale";
  fuelType?: string;
  locationQuery?: string;
  limit?: number;
  offset?: number;
}

interface TrendOptions {
  year?: number;
  fuelType?: string;
}

interface RollupOptions {
  level?: "city" | "region";
  fuelType?: string;
}

function emptyDashboardSummary(): EwuraFuelDashboardSummaryRead {
  return {
    latest_summary: null,
    latest_prices_preview: [],
    current_year_trends: [],
    available_months: [],
    insights: [],
  };
}

function emptyFilters(): EwuraFuelFiltersRead {
  return {
    fuel_types: [],
    market_segments: [],
    retail_history_years: [],
    wholesale_history_years: [],
    retail_latest_snapshot_date: null,
    retail_latest_snapshot_month_label: null,
    wholesale_latest_snapshot_date: null,
    wholesale_latest_snapshot_month_label: null,
  };
}

/** Ensures list fields exist when the API returns a partial or legacy payload. */
function normalizeEwuraFuelFilters(
  raw: Partial<EwuraFuelFiltersRead> | EwuraFuelFiltersRead,
): EwuraFuelFiltersRead {
  const fallback = emptyFilters();
  return {
    fuel_types: Array.isArray(raw.fuel_types) ? raw.fuel_types : fallback.fuel_types,
    market_segments: Array.isArray(raw.market_segments) ? raw.market_segments : fallback.market_segments,
    retail_history_years: Array.isArray(raw.retail_history_years)
      ? raw.retail_history_years
      : fallback.retail_history_years,
    wholesale_history_years: Array.isArray(raw.wholesale_history_years)
      ? raw.wholesale_history_years
      : fallback.wholesale_history_years,
    retail_latest_snapshot_date: raw.retail_latest_snapshot_date ?? null,
    retail_latest_snapshot_month_label: raw.retail_latest_snapshot_month_label ?? null,
    wholesale_latest_snapshot_date: raw.wholesale_latest_snapshot_date ?? null,
    wholesale_latest_snapshot_month_label: raw.wholesale_latest_snapshot_month_label ?? null,
  };
}

function emptyLatestPricePage(limit = ENERGY_DEFAULTS.latestPricesLimit): EwuraFuelLatestPricePage {
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

function emptyObservationPage(limit = ENERGY_DEFAULTS.historyLimit): EwuraFuelObservationPage {
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

async function safeRequest<T>(loader: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await loader();
  } catch {
    return fallback;
  }
}

export async function getEnergyDashboardSummary(): Promise<EwuraFuelDashboardSummaryRead> {
  return apiFetch<EwuraFuelDashboardSummaryRead>(API_ENDPOINTS.energy.ewura.dashboardSummary);
}

export async function getEnergyLatestPrices(
  options: LatestPricesOptions = {},
): Promise<EwuraFuelLatestPricePage> {
  return apiFetch<EwuraFuelLatestPricePage>(API_ENDPOINTS.energy.ewura.latestPrices, {
    query: {
      market_segment: options.marketSegment ?? "retail",
      limit: options.limit ?? ENERGY_DEFAULTS.latestPricesLimit,
      offset: options.offset ?? 0,
      fuel_type: options.fuelType,
      location_query: options.locationQuery,
    },
  });
}

export async function getEnergyCurrentYearTrends(
  options: TrendOptions = {},
): Promise<EwuraFuelMonthlyTrendRead[]> {
  return apiFetch<EwuraFuelMonthlyTrendRead[]>(API_ENDPOINTS.energy.ewura.currentYearTrends, {
    query: {
      year: options.year,
      fuel_type: options.fuelType,
    },
  });
}

export async function getEnergyHistory(
  options: HistoryOptions = {},
): Promise<EwuraFuelObservationPage> {
  return apiFetch<EwuraFuelObservationPage>(API_ENDPOINTS.energy.ewura.history, {
    query: {
      market_segment: options.marketSegment ?? "retail",
      year: options.year,
      fuel_type: options.fuelType,
      location_query: options.locationQuery,
      limit: options.limit ?? ENERGY_DEFAULTS.historyLimit,
      offset: options.offset ?? 0,
    },
  });
}

export async function getEnergyAvailableMonths(): Promise<EwuraFuelAvailableMonthRead[]> {
  return apiFetch<EwuraFuelAvailableMonthRead[]>(API_ENDPOINTS.energy.ewura.availableMonths);
}

export async function getEnergyFilters(): Promise<EwuraFuelFiltersRead> {
  return apiFetch<EwuraFuelFiltersRead>(API_ENDPOINTS.energy.ewura.filters);
}

export async function getEnergyRollups(
  options: RollupOptions = {},
): Promise<EwuraFuelRollupRead[]> {
  return apiFetch<EwuraFuelRollupRead[]>(API_ENDPOINTS.energy.ewura.rollups, {
    query: {
      level: options.level ?? ENERGY_DEFAULTS.rollupLevel,
      fuel_type: options.fuelType,
    },
  });
}

export async function getEnergyLatestExtremes(
  fuelType?: string,
): Promise<EwuraFuelLatestExtremesRead | null> {
  return apiFetch<EwuraFuelLatestExtremesRead | null>(API_ENDPOINTS.energy.ewura.latestExtremes, {
    query: {
      fuel_type: fuelType,
    },
  });
}

export async function getEnergyInsights(): Promise<EwuraFuelInsightRead[]> {
  return apiFetch<EwuraFuelInsightRead[]>(API_ENDPOINTS.energy.ewura.insights);
}

export async function getEnergyPageData(query: EnergyQueryState): Promise<EnergyPageData> {
  const [
    dashboardSummary,
    retailLatestPrices,
    wholesaleLatestPrices,
    currentYearTrends,
    retailHistory,
    wholesaleHistory,
    filters,
    availableMonths,
    rollups,
    latestExtremes,
    insights,
  ] = await Promise.all([
    safeRequest(getEnergyDashboardSummary, emptyDashboardSummary()),
    safeRequest(
      () =>
        getEnergyLatestPrices({
          marketSegment: "retail",
          fuelType: query.fuelType,
          locationQuery: query.locationQuery,
          limit: ENERGY_DEFAULTS.latestPricesLimit,
          offset: query.retailLatestOffset,
        }),
      emptyLatestPricePage(),
    ),
    safeRequest(
      () =>
        getEnergyLatestPrices({
          marketSegment: "wholesale",
          fuelType: query.fuelType,
          locationQuery: query.locationQuery,
          limit: ENERGY_DEFAULTS.latestPricesLimit,
          offset: query.wholesaleLatestOffset,
        }),
      emptyLatestPricePage(),
    ),
    safeRequest(() => getEnergyCurrentYearTrends({ fuelType: query.fuelType }), []),
    safeRequest(
      () =>
        query.retailHistoryYear
          ? getEnergyHistory({
              marketSegment: "retail",
              year: query.retailHistoryYear,
              fuelType: query.fuelType,
              locationQuery: query.locationQuery,
              limit: ENERGY_DEFAULTS.historyLimit,
              offset: query.retailHistoryOffset,
            })
          : Promise.resolve(emptyObservationPage()),
      emptyObservationPage(),
    ),
    safeRequest(
      () =>
        query.wholesaleHistoryYear
          ? getEnergyHistory({
              marketSegment: "wholesale",
              year: query.wholesaleHistoryYear,
              fuelType: query.fuelType,
              locationQuery: query.locationQuery,
              limit: ENERGY_DEFAULTS.historyLimit,
              offset: query.wholesaleHistoryOffset,
            })
          : Promise.resolve(emptyObservationPage()),
      emptyObservationPage(),
    ),
    safeRequest(getEnergyFilters, emptyFilters()).then(normalizeEwuraFuelFilters),
    safeRequest(getEnergyAvailableMonths, []),
    safeRequest(() => getEnergyRollups({ fuelType: query.fuelType }), []),
    safeRequest(() => getEnergyLatestExtremes(query.fuelType), null),
    safeRequest(getEnergyInsights, []),
  ]);

  return {
    dashboardSummary,
    retailLatestPrices,
    wholesaleLatestPrices,
    currentYearTrends,
    retailHistory,
    wholesaleHistory,
    filters,
    query,
    availableMonths,
    rollups,
    latestExtremes,
    insights,
  };
}
