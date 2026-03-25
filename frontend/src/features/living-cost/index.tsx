"use client";

import type { LandPrice, RentPrice } from "@/types/api";
import { LandTable } from "./components/land-table";
import { RentTable } from "./components/rent-table";

interface LivingCostFeatureProps {
  rentPrices: RentPrice[];
  landPrices: LandPrice[];
}

export function LivingCostFeature({ rentPrices, landPrices }: LivingCostFeatureProps) {
  return (
    <div className="space-y-8">
      <RentTable data={rentPrices} />
      <LandTable data={landPrices} />
    </div>
  );
}
