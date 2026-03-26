import { drugPrices } from "@/data/medicine";
import type { DrugPrice } from "@/types/api";
import { simulateFetch } from "./api-client";

export async function getDrugPrices(): Promise<DrugPrice[]> {
  return simulateFetch(drugPrices);
}
