export const ROUTES = {
  dashboard: "/data",
  energy: "/energy",
  energyMonitoring: "/energy/monitoring",
  money: "/money",
  dse: "/dse",
  livingCost: "/living-cost",
  medicine: "/medicine",
  hr: "/hr",
} as const;

export type RouteKey = keyof typeof ROUTES;

export const NAV_ITEMS: { key: RouteKey; translationKey: string; icon: string; disabled?: boolean }[] = [
  { key: "dashboard", translationKey: "nav.dashboard", icon: "grid" },
  { key: "energy", translationKey: "nav.energy", icon: "zap" },
  { key: "money", translationKey: "nav.money", icon: "banknote" },
  { key: "dse", translationKey: "nav.dse", icon: "trending-up" },
  { key: "livingCost", translationKey: "nav.livingCost", icon: "home", disabled: true },
  { key: "medicine", translationKey: "nav.medicine", icon: "pill", disabled: true },
  { key: "hr", translationKey: "nav.hr", icon: "users", disabled: true },
  { key: "energyMonitoring", translationKey: "nav.monitoring", icon: "activity" },
];

export const CURRENCY = "TZS";

export const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function resolveApiBaseUrl(): string {
  const configuredUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (configuredUrl) {
    return configuredUrl.replace(/\/$/, "");
  }

  if (process.env.NODE_ENV === "production") {
    throw new Error("NEXT_PUBLIC_API_URL must be set in production.");
  }

  return DEFAULT_API_BASE_URL;
}

export const API_BASE_URL = resolveApiBaseUrl();

export const API_ENDPOINTS = {
  energy: {
    ewura: {
      dashboardSummary: "/energy/fuel/ewura/dashboard-summary",
      latestPrices: "/energy/fuel/ewura/latest",
      currentYearTrends: "/energy/fuel/ewura/current-year",
      history: "/energy/fuel/ewura/history",
      availableMonths: "/energy/fuel/ewura/available-months",
      filters: "/energy/fuel/ewura/filters",
      rollups: "/energy/fuel/ewura/rollups",
      latestExtremes: "/energy/fuel/ewura/latest-extremes",
      insights: "/energy/fuel/ewura/insights",
      runs: "/energy/fuel/ewura/runs",
    },
  },
  dse: {
    dashboardSummary: "/money/stocks/dse/dashboard-summary",
    latest: "/money/stocks/dse/latest",
    history: "/money/stocks/dse/history",
  },
  money: {
    exchangeRates: {
      dashboardSummary: "/money/exchange-rates/dashboard-summary",
      botFilters: "/money/exchange-rates/bot/filters",
      botHistory: "/money/exchange-rates/bot/history",
      latestComparison: "/money/exchange-rates/latest-comparison",
      recommendation: "/money/exchange-rates/recommendation",
      spreads: "/money/exchange-rates/analytics/spreads",
      benchmarkGaps: "/money/exchange-rates/analytics/benchmark-gaps",
      staleness: "/money/exchange-rates/analytics/staleness",
      bestRates: "/money/exchange-rates/analytics/best-rates",
      opportunities: "/money/exchange-rates/analytics/opportunities",
    },
  },
} as const;

export const API_DEFAULT_REVALIDATE_SECONDS = 3600;

export const API_STATIC_REVALIDATE_SECONDS = 86400;

export const ENERGY_DEFAULTS = {
  latestPricesLimit: 12,
  historyLimit: 12,
  runsLimit: 5,
  runLogsLimit: 8,
  rollupsLimit: 12,
  rollupLevel: "region",
} as const;

export const MONEY_DEFAULTS = {
  defaultInstrumentCode: "USD",
  historyLimit: 12,
  quickInstrumentLimit: 12,
} as const;
