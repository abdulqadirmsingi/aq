"use client";

import type { DrugPrice } from "@/types/api";
import { DrugPriceTable } from "./components/drug-price-table";

interface MedicineFeatureProps {
  drugPrices: DrugPrice[];
}

export function MedicineFeature({ drugPrices }: MedicineFeatureProps) {
  return (
    <div className="space-y-8">
      <DrugPriceTable data={drugPrices} />
    </div>
  );
}
