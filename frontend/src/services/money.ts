import { exchangeRates, inflationRecords } from "@/data/money";
import type { ExchangeRate, InflationRecord } from "@/types/api";
import { simulateFetch } from "./api-client";

export async function getExchangeRates(): Promise<ExchangeRate[]> {
  return simulateFetch(exchangeRates);
}

export async function getInflationRecords(): Promise<InflationRecord[]> {
  return simulateFetch(inflationRecords);
}
