import { salaries } from "@/data/hr";
import { rentPrices } from "@/data/living-cost";
import { drugPrices } from "@/data/medicine";
import { exchangeRates } from "@/data/money";
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

  const usd = exchangeRates.find((r) => r.currencyPair === "USD/TZS");

  const avgRent =
    rentPrices.reduce((sum, r) => sum + r.monthlyRent, 0) / rentPrices.length;
  const avgRentPrev =
    rentPrices.reduce((sum, r) => sum + r.previousRent, 0) / rentPrices.length;

  const avgDrug =
    drugPrices.reduce((sum, d) => sum + (d.minPrice + d.maxPrice) / 2, 0) / drugPrices.length;

  const avgSalary =
    salaries.reduce((sum, s) => sum + s.avgSalary, 0) / salaries.length;

  return [
    {
      label: "dashboard.fuelAvgPrice",
      value: currentAverage > 0 ? `${formatNumber(Math.round(currentAverage))} TZS` : "N/A",
      change: computeChangePercent(currentAverage, previousAverage),
      trend: computeTrend(currentAverage, previousAverage),
    },
    {
      label: "dashboard.exchangeRate",
      value: usd ? `${formatNumber(usd.buyRate)} TZS` : "N/A",
      change: usd ? computeChangePercent(usd.buyRate, usd.previousBuyRate) : 0,
      trend: usd ? computeTrend(usd.buyRate, usd.previousBuyRate) : "stable",
    },
    {
      label: "dashboard.avgRent",
      value: `${formatNumber(Math.round(avgRent))} TZS`,
      change: computeChangePercent(avgRent, avgRentPrev),
      trend: computeTrend(avgRent, avgRentPrev),
    },
    {
      label: "dashboard.drugPriceIndex",
      value: `${formatNumber(Math.round(avgDrug))} TZS`,
      trend: "stable",
      change: 0,
    },
    {
      label: "dashboard.avgSalary",
      value: `${formatNumber(Math.round(avgSalary))} TZS`,
      trend: "stable",
      change: 0,
    },
  ];
}

export async function getDashboardSummaries(): Promise<DomainSummary[]> {
  const fuelSummary = await getEnergyDashboardSummary().catch(() => null);
  return simulateFetch(buildSummaries(fuelSummary));
}
