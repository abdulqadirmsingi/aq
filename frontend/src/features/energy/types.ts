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
  retailHistoryYear?: number;
  wholesaleHistoryYear?: number;
  retailLatestOffset: number;
  retailHistoryOffset: number;
  wholesaleLatestOffset: number;
  wholesaleHistoryOffset: number;
}

export interface EnergyPageData {
  dashboardSummary: EwuraFuelDashboardSummaryRead;
  retailLatestPrices: EwuraFuelLatestPricePage;
  wholesaleLatestPrices: EwuraFuelLatestPricePage;
  currentYearTrends: EwuraFuelMonthlyTrendRead[];
  retailHistory: EwuraFuelObservationPage;
  wholesaleHistory: EwuraFuelObservationPage;
  filters: EwuraFuelFiltersRead;
  query: EnergyQueryState;
  availableMonths: EwuraFuelAvailableMonthRead[];
  rollups: EwuraFuelRollupRead[];
  latestExtremes: EwuraFuelLatestExtremesRead | null;
  insights: EwuraFuelInsightRead[];
}
