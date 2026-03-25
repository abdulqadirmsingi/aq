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

  if (next.activeTab && next.activeTab !== "overview") {
    params.set("tab", next.activeTab);
  }
  if (next.fuelType) {
    params.set("fuelType", next.fuelType);
  }
  if (next.locationQuery) {
    params.set("locationQuery", next.locationQuery);
  }
  if (next.retailHistoryYear) {
    params.set("retailHistoryYear", String(next.retailHistoryYear));
  }
  if (next.wholesaleHistoryYear) {
    params.set("wholesaleHistoryYear", String(next.wholesaleHistoryYear));
  }
  if (next.retailLatestOffset > 0) {
    params.set("retailLatestOffset", String(next.retailLatestOffset));
  }
  if (next.retailHistoryOffset > 0) {
    params.set("retailHistoryOffset", String(next.retailHistoryOffset));
  }
  if (next.wholesaleLatestOffset > 0) {
    params.set("wholesaleLatestOffset", String(next.wholesaleLatestOffset));
  }
  if (next.wholesaleHistoryOffset > 0) {
    params.set("wholesaleHistoryOffset", String(next.wholesaleHistoryOffset));
  }
  if (next.rollupsOffset > 0) {
    params.set("rollupsOffset", String(next.rollupsOffset));
  }

  const queryString = params.toString();
  return queryString ? `${ROUTES.energy}?${queryString}` : ROUTES.energy;
}
