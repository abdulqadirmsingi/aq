import type { Metadata } from "next";
import { ProcurementFeature } from "@/features/procurement";
import { getProcurementPageData } from "@/services/procurement";
import { buildPageMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "Public Procurement",
  description:
    "Tanzania government tenders and contract awards from the NeST PPRA system — OCDS-compliant open data.",
  path: "/procurement",
  keywords: ["procurement", "Tanzania tenders", "PPRA", "NeST", "government contracts", "OCDS"],
});

export const revalidate = 3600;

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function readOffset(params: Record<string, string | string[] | undefined>): number {
  const raw = Array.isArray(params.offset) ? params.offset[0] : params.offset;
  const parsed = Number.parseInt(raw ?? "0", 10);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
}

export default async function ProcurementPage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const offset = readOffset(params);
  const { tenders, filters } = await getProcurementPageData({ offset });

  return (
    <div className="space-y-10">
      <ProcurementFeature tenders={tenders} filters={filters} offset={offset} />
    </div>
  );
}
