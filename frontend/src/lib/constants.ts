export const ROUTES = {
  dashboard: "/",
  energy: "/energy",
  money: "/money",
  livingCost: "/living-cost",
  medicine: "/medicine",
  hr: "/hr",
} as const;

export type RouteKey = keyof typeof ROUTES;

export const NAV_ITEMS: { key: RouteKey; translationKey: string; icon: string }[] = [
  { key: "dashboard", translationKey: "nav.dashboard", icon: "grid" },
  { key: "energy", translationKey: "nav.energy", icon: "zap" },
  { key: "money", translationKey: "nav.money", icon: "banknote" },
  { key: "livingCost", translationKey: "nav.livingCost", icon: "home" },
  { key: "medicine", translationKey: "nav.medicine", icon: "pill" },
  { key: "hr", translationKey: "nav.hr", icon: "users" },
];

export const CURRENCY = "TZS";

export const SIMULATED_DELAY_MS = 300;
