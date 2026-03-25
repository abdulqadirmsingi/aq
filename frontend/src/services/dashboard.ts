import { fuelPrices } from "@/data/energy";
import { salaries } from "@/data/hr";
import { rentPrices } from "@/data/living-cost";
import { drugPrices } from "@/data/medicine";
import { exchangeRates } from "@/data/money";
import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { DomainSummary } from "@/types";
import { simulateFetch } from "./api-client";

function buildSummaries(): DomainSummary[] {
  const avgFuel =
    fuelPrices.reduce((sum, f) => sum + f.pricePerLitre, 0) / fuelPrices.length;
  const avgFuelPrev =
    fuelPrices.reduce((sum, f) => sum + f.previousPrice, 0) / fuelPrices.length;

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
      value: `${formatNumber(Math.round(avgFuel))} TZS`,
      change: computeChangePercent(avgFuel, avgFuelPrev),
      trend: computeTrend(avgFuel, avgFuelPrev),
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
  return simulateFetch(buildSummaries());
}
