import type { Metadata } from "next";
import { EnergyMonitoringFeature } from "@/features/energy-monitoring";
import { buildPageMetadata } from "@/lib/seo";
import { getEnergyMonitoringPageData } from "@/services/energy-monitoring";

export const metadata: Metadata = buildPageMetadata({
  title: "Scraper Monitoring",
  description:
    "Monitor EWURA ingestion runs, scraper health, and operational logs for AQ's energy pipeline.",
  path: "/energy/monitoring",
  imageTitle: "AQ Scraper Monitoring",
  imageDetail: "Operational visibility for EWURA ingestion runs and data pipeline health.",
  keywords: ["data pipeline monitoring", "scraper health", "EWURA ingestion"],
});

export default async function EnergyMonitoringPage() {
  const data = await getEnergyMonitoringPageData();

  return <EnergyMonitoringFeature data={data} />;
}
