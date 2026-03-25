import { landPrices, rentPrices } from "@/data/living-cost";
import type { LandPrice, RentPrice } from "@/types/api";
import { simulateFetch } from "./api-client";

export async function getRentPrices(): Promise<RentPrice[]> {
  return simulateFetch(rentPrices);
}

export async function getLandPrices(): Promise<LandPrice[]> {
  return simulateFetch(landPrices);
}
