"use client";

import type { ExchangeRate, InflationRecord } from "@/types/api";
import { ExchangeRateTable } from "./components/exchange-rate-table";
import { InflationTable } from "./components/inflation-table";

interface MoneyFeatureProps {
  exchangeRates: ExchangeRate[];
  inflationRecords: InflationRecord[];
}

export function MoneyFeature({ exchangeRates, inflationRecords }: MoneyFeatureProps) {
  return (
    <div className="space-y-8">
      <ExchangeRateTable data={exchangeRates} />
      <InflationTable data={inflationRecords} />
    </div>
  );
}
