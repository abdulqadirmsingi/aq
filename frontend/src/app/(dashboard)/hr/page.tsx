import type { Metadata } from "next";
import { HrFeature } from "@/features/hr";
import { buildPageMetadata } from "@/lib/seo";
import { getJobTrends, getSalaries } from "@/services/hr";

export const metadata: Metadata = buildPageMetadata({
  title: "Labour Market Signals",
  description:
    "Explore job trend and salary snapshots through a clean workforce intelligence view in AQ.",
  path: "/hr",
  imageTitle: "Labour Market Signals",
  imageDetail: "Workforce trends and salary signals presented in a share-ready AQ format.",
  keywords: ["job trends", "salary data", "labour market", "HR analytics"],
});

export const revalidate = 86400;

export default async function HrPage() {
  const [salaries, jobTrends] = await Promise.all([getSalaries(), getJobTrends()]);

  return (
    <div className="space-y-10">
      <HrFeature salaries={salaries} jobTrends={jobTrends} />
    </div>
  );
}
