import { EnergyFeature } from "@/features/energy";
import { getElectricityTariffs, getFuelPrices, getGasPrices } from "@/services/energy";

export default async function EnergyPage() {
  const [fuelPrices, gasPrices, electricityTariffs] = await Promise.all([
    getFuelPrices(),
    getGasPrices(),
    getElectricityTariffs(),
  ]);

  return (
    <>
      <EnergyFeature
        fuelPrices={fuelPrices}
        gasPrices={gasPrices}
        electricityTariffs={electricityTariffs}
      />
    </>
  );
}
