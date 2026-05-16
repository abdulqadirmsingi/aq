import type { Metadata } from "next";
import { DseFeature } from "@/features/dse";
import { getDsePageData } from "@/services/dse";
import { buildPageMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "DSE Stock Market",
  description:
    "Live Dar es Salaam Stock Exchange data — daily OHLCV prices, gainers, losers, and turnover for all listed equities and ETFs.",
  path: "/dse",
  keywords: ["DSE", "Tanzania stock market", "Dar es Salaam Stock Exchange", "TZS stocks"],
});

export const revalidate = 3600;

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function readOffset(params: Record<string, string | string[] | undefined>): number {
  const raw = Array.isArray(params.offset) ? params.offset[0] : params.offset;
  const parsed = Number.parseInt(raw ?? "0", 10);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
}

export default async function DsePage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const offset = readOffset(params);
  const data = await getDsePageData(offset);
  return <DseFeature data={data} offset={offset} />;
}
