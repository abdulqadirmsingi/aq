import type { Metadata } from "next";
import { MoneyFeature } from "@/features/money";
import { getMoneyPageData } from "@/services/money";
import type {
  MoneyCashNoteBand,
  MoneyChannel,
  MoneyCustomerAction,
  MoneyQueryState,
} from "@/features/money/types";
import { buildPageMetadata, readQueryValue } from "@/lib/seo";

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

export async function generateMetadata({
  searchParams,
}: MoneyPageProps): Promise<Metadata> {
  const params = await searchParams;
  const instrumentCode = readQueryValue(params.instrumentCode) ?? "USD";
  const customerAction = readCustomerAction(params.customerAction);
  const channel = readChannel(params.channel);

  const title = `${instrumentCode} Exchange Rates`;
  const channelLabel = channel ? ` via ${channel.replaceAll("_", " ")}` : "";
  const detail = `${customerAction === "buy" ? "Buying" : "Selling"} ${instrumentCode}${channelLabel}`.replace(
    /^./,
    (letter) => letter.toUpperCase(),
  );

  return buildPageMetadata({
    title,
    description: `Compare BOT, CRDB, and NMB foreign exchange signals for ${instrumentCode} in one AQ view.`,
    path: "/money",
    query: params,
    imageTitle: title,
    imageDetail: detail,
    keywords: ["forex dashboard", "Tanzania exchange rates", `${instrumentCode} TZS`],
  });
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
