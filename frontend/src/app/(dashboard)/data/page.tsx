import type { Metadata } from "next";
import { DashboardFeature } from "@/features/dashboard";
import { buildPageMetadata } from "@/lib/seo";
import { getDashboardSummaries } from "@/services/dashboard";

export const revalidate = 3600;

export const metadata: Metadata = buildPageMetadata({
  title: "Tanzania Data Dashboard",
  description:
    "A multi-sector view of Tanzania's historical records, current signals, and decision-ready intelligence.",
  path: "/",
  imageTitle: "Tanzania Data Dashboard",
  imageDetail: "Historical records and current signals in one decision-ready intelligence workspace.",
});

export default async function DashboardPage() {
  const summaries = await getDashboardSummaries();

  return (
    <div className="space-y-10">
      <DashboardFeature summaries={summaries} />
    </div>
  );
}
