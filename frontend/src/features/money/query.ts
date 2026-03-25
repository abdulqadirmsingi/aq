import { ROUTES } from "@/lib/constants";
import type { MoneyQueryState } from "./types";

export function buildMoneyHref(
  query: Partial<MoneyQueryState>,
  base: MoneyQueryState,
): string {
  const params = new URLSearchParams();
  const next = {
    ...base,
    ...query,
  };

  if (next.instrumentCode) {
    params.set("instrumentCode", next.instrumentCode);
  }
  if (next.customerAction !== "buy") {
    params.set("customerAction", next.customerAction);
  }
  if (next.channel) {
    params.set("channel", next.channel);
  }
  if (next.cashNoteBand) {
    params.set("cashNoteBand", next.cashNoteBand);
  }
  if (next.historyOffset > 0) {
    params.set("historyOffset", String(next.historyOffset));
  }

  const queryString = params.toString();
  return queryString ? `${ROUTES.money}?${queryString}` : ROUTES.money;
}
