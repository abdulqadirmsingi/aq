import type {
  EwuraFuelAvailableMonthRead,
  EwuraFuelDashboardSummaryRead,
  EwuraFuelFiltersRead,
  EwuraFuelInsightRead,
  EwuraFuelLatestExtremesRead,
  EwuraFuelLatestPricePage,
  EwuraFuelMonthlyTrendRead,
  EwuraFuelObservationPage,
  EwuraFuelRollupPage,
} from "@/types/api";

export type EnergyTabId = "overview" | "retail" | "wholesale" | "rollups" | "insights";

export interface EnergyQueryState {
  activeTab: EnergyTabId;
  fuelType?: string;
  locationQuery?: string;
  retailHistoryYear?: number;
  wholesaleHistoryYear?: number;
  retailLatestOffset: number;
  retailHistoryOffset: number;
  wholesaleLatestOffset: number;
  wholesaleHistoryOffset: number;
  rollupsOffset: number;
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
  rollups: EwuraFuelRollupPage;
  latestExtremes: EwuraFuelLatestExtremesRead | null;
  insights: EwuraFuelInsightRead[];
}
