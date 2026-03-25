import { EnergyMonitoringFeature } from "@/features/energy-monitoring";
import { getEnergyMonitoringPageData } from "@/services/energy-monitoring";

export default async function EnergyMonitoringPage() {
  const data = await getEnergyMonitoringPageData();

  return <EnergyMonitoringFeature data={data} />;
}
