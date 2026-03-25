"use client";

import type { ElectricityTariff, FuelPrice, GasPrice } from "@/types/api";
import { ElectricityTariffTable } from "./components/electricity-tariff-table";
import { FuelPriceTable } from "./components/fuel-price-table";
import { GasPriceTable } from "./components/gas-price-table";

interface EnergyFeatureProps {
  fuelPrices: FuelPrice[];
  gasPrices: GasPrice[];
  electricityTariffs: ElectricityTariff[];
}

export function EnergyFeature({ fuelPrices, gasPrices, electricityTariffs }: EnergyFeatureProps) {
  return (
    <div className="space-y-8">
      <FuelPriceTable data={fuelPrices} />
      <GasPriceTable data={gasPrices} />
      <ElectricityTariffTable data={electricityTariffs} />
    </div>
  );
}
