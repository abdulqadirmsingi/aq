import { electricityTariffs, fuelPrices, gasPrices } from "@/data/energy";
import type { ElectricityTariff, FuelPrice, GasPrice } from "@/types/api";
import { simulateFetch } from "./api-client";

export async function getFuelPrices(): Promise<FuelPrice[]> {
  return simulateFetch(fuelPrices);
}

export async function getGasPrices(): Promise<GasPrice[]> {
  return simulateFetch(gasPrices);
}

export async function getElectricityTariffs(): Promise<ElectricityTariff[]> {
  return simulateFetch(electricityTariffs);
}
