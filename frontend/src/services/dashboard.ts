import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { DomainSummary } from "@/types";
import { simulateFetch } from "./api-client";
import { getEnergyDashboardSummary } from "./energy";

function getFuelSummaryMetrics(summary: Awaited<ReturnType<typeof getEnergyDashboardSummary>>) {
  const summaryItems = summary.latest_summary?.items ?? [];
  const currentAverage =
    summaryItems.length > 0
      ? summaryItems.reduce((sum, item) => sum + item.avg_price, 0) / summaryItems.length
      : 0;
  const previousPrices = summary.latest_prices_preview
    .map((item) => item.previous_price)
    .filter((item): item is number => item !== null);
  const previousAverage =
    previousPrices.length > 0
      ? previousPrices.reduce((sum, item) => sum + item, 0) / previousPrices.length
      : currentAverage;

  return { currentAverage, previousAverage };
}

function buildSummaries(
  fuelSummary: Awaited<ReturnType<typeof getEnergyDashboardSummary>> | null,
): DomainSummary[] {
  const { currentAverage, previousAverage } = fuelSummary
    ? getFuelSummaryMetrics(fuelSummary)
    : { currentAverage: 0, previousAverage: 0 };

  return [
    {
      label: "dashboard.fuelAvgPrice",
      value: currentAverage > 0 ? `${formatNumber(Math.round(currentAverage))} TZS` : "N/A",
      change: computeChangePercent(currentAverage, previousAverage),
      trend: computeTrend(currentAverage, previousAverage),
    },
    // Exchange rates disabled for now as requested
    /*
    {
      label: "dashboard.exchangeRate",
      value: usd ? `${formatNumber(usd.buyRate)} TZS` : "N/A",
      change: usd ? computeChangePercent(usd.buyRate, usd.previousBuyRate) : 0,
      trend: usd ? computeTrend(usd.buyRate, usd.previousBuyRate) : "stable",
    },
    */
  ];
}

export async function getDashboardSummaries(): Promise<DomainSummary[]> {
  const fuelSummary = await getEnergyDashboardSummary().catch(() => null);
  return simulateFetch(buildSummaries(fuelSummary));
}
