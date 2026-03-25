import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { DomainSummary } from "@/types";
import { simulateFetch } from "./api-client";
import { getEnergyDashboardSummary } from "./energy";
import { getMoneyDashboardSummary } from "./money";

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
  moneySummary: Awaited<ReturnType<typeof getMoneyDashboardSummary>> | null,
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
    {
      label: "dashboard.exchangeRate",
      value:
        moneySummary?.bot_mean_rate !== null && moneySummary?.bot_mean_rate !== undefined
          ? `${formatNumber(Math.round(moneySummary.bot_mean_rate))} TZS`
          : "N/A",
      subtitle: moneySummary?.instrument_code ? `BOT ${moneySummary.instrument_code}/TZS` : undefined,
    },
    {
      label: "money.bestPlaceToBuy",
      value: moneySummary?.buy_best_source_name ?? "N/A",
      subtitle:
        moneySummary?.buy_best_rate !== null && moneySummary?.buy_best_rate !== undefined
          ? `${formatNumber(Math.round(moneySummary.buy_best_rate))} TZS`
          : undefined,
    },
    {
      label: "money.bestPlaceToSell",
      value: moneySummary?.sell_best_source_name ?? "N/A",
      subtitle:
        moneySummary?.sell_best_rate !== null && moneySummary?.sell_best_rate !== undefined
          ? `${formatNumber(Math.round(moneySummary.sell_best_rate))} TZS`
          : undefined,
    },
    {
      label: "money.freshestSource",
      value: moneySummary?.freshest_source_name ?? "N/A",
      subtitle:
        moneySummary?.comparison_sources_count !== null
          && moneySummary?.comparison_sources_count !== undefined
          ? `${moneySummary.comparison_sources_count} sources`
          : undefined,
    },
  ];
}

export async function getDashboardSummaries(): Promise<DomainSummary[]> {
  const fuelSummary = await getEnergyDashboardSummary().catch(() => null);
  const moneySummary = await getMoneyDashboardSummary().catch(() => null);
  return simulateFetch(buildSummaries(fuelSummary, moneySummary));
}
