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

export default async function DsePage() {
  const data = await getDsePageData();
  return <DseFeature data={data} />;
}
