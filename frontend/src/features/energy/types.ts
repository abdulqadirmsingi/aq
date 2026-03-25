import type {
  EwuraFuelAvailableMonthRead,
  EwuraFuelDashboardSummaryRead,
  EwuraFuelInsightRead,
  EwuraFuelLatestExtremesRead,
  EwuraFuelLatestPriceRead,
  EwuraFuelMonthlyTrendRead,
  EwuraFuelObservationPage,
  EwuraFuelRollupRead,
  EwuraFuelRunLogPage,
  EwuraFuelRunPage,
} from "@/types/api";

export interface EnergyPageData {
  dashboardSummary: EwuraFuelDashboardSummaryRead;
  latestPrices: EwuraFuelLatestPriceRead[];
  currentYearTrends: EwuraFuelMonthlyTrendRead[];
  history: EwuraFuelObservationPage;
  availableMonths: EwuraFuelAvailableMonthRead[];
  rollups: EwuraFuelRollupRead[];
  latestExtremes: EwuraFuelLatestExtremesRead | null;
  insights: EwuraFuelInsightRead[];
  runs: EwuraFuelRunPage;
  runLogs: EwuraFuelRunLogPage | null;
}
