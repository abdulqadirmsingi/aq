export const ROUTES = {
  dashboard: "/",
  energy: "/energy",
  energyMonitoring: "/energy/monitoring",
  money: "/money",
  livingCost: "/living-cost",
  medicine: "/medicine",
  hr: "/hr",
} as const;

export type RouteKey = keyof typeof ROUTES;

export const NAV_ITEMS: { key: RouteKey; translationKey: string; icon: string }[] = [
  { key: "dashboard", translationKey: "nav.dashboard", icon: "grid" },
  { key: "energy", translationKey: "nav.energy", icon: "zap" },
  { key: "energyMonitoring", translationKey: "nav.energyMonitoring", icon: "activity" },
  { key: "money", translationKey: "nav.money", icon: "banknote" },
  { key: "livingCost", translationKey: "nav.livingCost", icon: "home" },
  { key: "medicine", translationKey: "nav.medicine", icon: "pill" },
  { key: "hr", translationKey: "nav.hr", icon: "users" },
];

export const CURRENCY = "TZS";

export const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_BASE_URL;

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
} as const;

export const API_DEFAULT_REVALIDATE_SECONDS = 300;

export const ENERGY_DEFAULTS = {
  latestPricesLimit: 12,
  historyLimit: 12,
  runsLimit: 5,
  runLogsLimit: 8,
  rollupLevel: "region",
} as const;
