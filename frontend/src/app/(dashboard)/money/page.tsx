import { MoneyFeature } from "@/features/money";
import { getMoneyPageData } from "@/services/money";
import type {
  MoneyCashNoteBand,
  MoneyChannel,
  MoneyCustomerAction,
  MoneyQueryState,
} from "@/features/money/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

interface MoneyPageProps {
  searchParams: SearchParams;
}

function readSingleValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function readInt(value: string | string[] | undefined): number | undefined {
  const raw = readSingleValue(value);
  if (!raw) {
    return undefined;
  }
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : undefined;
}

function readCustomerAction(
  value: string | string[] | undefined,
): MoneyCustomerAction {
  const raw = readSingleValue(value);
  return raw === "sell" ? "sell" : "buy";
}

function readChannel(value: string | string[] | undefined): MoneyChannel | undefined {
  const raw = readSingleValue(value);
  if (raw === "counter" || raw === "non_cash" || raw === "cash") {
    return raw;
  }
  return undefined;
}

function readCashNoteBand(
  value: string | string[] | undefined,
): MoneyCashNoteBand | undefined {
  const raw = readSingleValue(value);
  if (raw === "notes_50_500" || raw === "notes_1_20") {
    return raw;
  }
  return undefined;
}

export default async function MoneyPage({ searchParams }: MoneyPageProps) {
  const params = await searchParams;
  const channel = readChannel(params.channel);
  const query: MoneyQueryState = {
    instrumentCode: readSingleValue(params.instrumentCode) ?? "USD",
    customerAction: readCustomerAction(params.customerAction),
    channel,
    cashNoteBand: channel === "cash" ? readCashNoteBand(params.cashNoteBand) : undefined,
    historyOffset: readInt(params.historyOffset) ?? 0,
  };
  const data = await getMoneyPageData(query);

  return <MoneyFeature data={data} />;
}
