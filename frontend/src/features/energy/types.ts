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

export interface EnergyQueryState {
  fuelType?: string;
  locationQuery?: string;
  historyYear?: number;
  latestOffset: number;
  historyOffset: number;
}

export interface EnergyPageData {
  dashboardSummary: EwuraFuelDashboardSummaryRead;
  latestPrices: EwuraFuelLatestPricePage;
  currentYearTrends: EwuraFuelMonthlyTrendRead[];
  history: EwuraFuelObservationPage;
  filters: EwuraFuelFiltersRead;
  query: EnergyQueryState;
  availableMonths: EwuraFuelAvailableMonthRead[];
  rollups: EwuraFuelRollupRead[];
  latestExtremes: EwuraFuelLatestExtremesRead | null;
  insights: EwuraFuelInsightRead[];
}
