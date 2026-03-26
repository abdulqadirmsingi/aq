import type { ExchangeRate, InflationRecord } from "@/types/api";

export const exchangeRates: ExchangeRate[] = [
  { id: "ex1", currencyPair: "USD/TZS", buyRate: 2655, sellRate: 2685, previousBuyRate: 2640, date: "2026-03-25" },
  { id: "ex2", currencyPair: "EUR/TZS", buyRate: 2890, sellRate: 2925, previousBuyRate: 2870, date: "2026-03-25" },
  { id: "ex3", currencyPair: "GBP/TZS", buyRate: 3380, sellRate: 3420, previousBuyRate: 3360, date: "2026-03-25" },
  { id: "ex4", currencyPair: "KES/TZS", buyRate: 20.5, sellRate: 21.2, previousBuyRate: 20.3, date: "2026-03-25" },
  { id: "ex5", currencyPair: "ZAR/TZS", buyRate: 147, sellRate: 152, previousBuyRate: 145, date: "2026-03-25" },
  { id: "ex6", currencyPair: "CNY/TZS", buyRate: 365, sellRate: 375, previousBuyRate: 362, date: "2026-03-25" },
];

export const inflationRecords: InflationRecord[] = [
  { id: "in1", month: "2026-03", rate: 3.8, previousRate: 3.6, yearOverYear: 3.8 },
  { id: "in2", month: "2026-02", rate: 3.6, previousRate: 3.5, yearOverYear: 3.6 },
  { id: "in3", month: "2026-01", rate: 3.5, previousRate: 3.4, yearOverYear: 3.5 },
  { id: "in4", month: "2025-12", rate: 3.4, previousRate: 3.3, yearOverYear: 3.4 },
  { id: "in5", month: "2025-11", rate: 3.3, previousRate: 3.2, yearOverYear: 3.3 },
  { id: "in6", month: "2025-10", rate: 3.2, previousRate: 3.1, yearOverYear: 3.2 },
];
