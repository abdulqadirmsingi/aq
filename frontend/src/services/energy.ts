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
  year?: number;
  fuelType?: string;
  locationQuery?: string;
  limit?: number;
  offset?: number;
}

interface LatestPricesOptions {
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
    history_years: [],
    latest_snapshot_date: null,
    latest_snapshot_month_label: null,
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
    latestPrices,
    currentYearTrends,
    history,
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
          fuelType: query.fuelType,
          locationQuery: query.locationQuery,
          limit: ENERGY_DEFAULTS.latestPricesLimit,
          offset: query.latestOffset,
        }),
      emptyLatestPricePage(),
    ),
    safeRequest(() => getEnergyCurrentYearTrends({ fuelType: query.fuelType }), []),
    safeRequest(
      () =>
        query.historyYear
          ? getEnergyHistory({
              year: query.historyYear,
              fuelType: query.fuelType,
              locationQuery: query.locationQuery,
              limit: ENERGY_DEFAULTS.historyLimit,
              offset: query.historyOffset,
            })
          : Promise.resolve(emptyObservationPage()),
      emptyObservationPage(),
    ),
    safeRequest(getEnergyFilters, emptyFilters()),
    safeRequest(getEnergyAvailableMonths, []),
    safeRequest(() => getEnergyRollups({ fuelType: query.fuelType }), []),
    safeRequest(() => getEnergyLatestExtremes(query.fuelType), null),
    safeRequest(getEnergyInsights, []),
  ]);

  return {
    dashboardSummary,
    latestPrices,
    currentYearTrends,
    history,
    filters,
    query,
    availableMonths,
    rollups,
    latestExtremes,
    insights,
  };
}
