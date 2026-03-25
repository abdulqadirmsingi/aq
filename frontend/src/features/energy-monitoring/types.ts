import type { EwuraFuelRunLogPage, EwuraFuelRunPage } from "@/types/api";

export interface EnergyMonitoringPageData {
  runs: EwuraFuelRunPage;
  runLogs: EwuraFuelRunLogPage | null;
}
