import { ROUTES } from "@/lib/constants";
import type { EnergyQueryState } from "./types";

export function buildEnergyHref(
  query: Partial<EnergyQueryState>,
  base: EnergyQueryState,
): string {
  const params = new URLSearchParams();
  const next = {
    ...base,
    ...query,
  };

  if (next.fuelType) {
    params.set("fuelType", next.fuelType);
  }
  if (next.locationQuery) {
    params.set("locationQuery", next.locationQuery);
  }
  if (next.historyYear) {
    params.set("historyYear", String(next.historyYear));
  }
  if (next.latestOffset > 0) {
    params.set("latestOffset", String(next.latestOffset));
  }
  if (next.historyOffset > 0) {
    params.set("historyOffset", String(next.historyOffset));
  }

  const queryString = params.toString();
  return queryString ? `${ROUTES.energy}?${queryString}` : ROUTES.energy;
}
