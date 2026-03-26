import { MonitoringSection } from "./components/monitoring-section";
import type { EnergyMonitoringPageData } from "./types";

interface EnergyMonitoringFeatureProps {
  data: EnergyMonitoringPageData;
}

export function EnergyMonitoringFeature({ data }: EnergyMonitoringFeatureProps) {
  return <MonitoringSection runs={data.runs} runLogs={data.runLogs} />;
}
