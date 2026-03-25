import { EnergyFeature } from "@/features/energy";
import { getElectricityTariffs, getFuelPrices, getGasPrices } from "@/services/energy";
import { getTranslations } from "next-intl/server";

export default async function EnergyPage() {
  const t = await getTranslations("energy");
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
