import { PageHeader } from "@/components/ui/page-header";
import { DashboardFeature } from "@/features/dashboard";
import { getDashboardSummaries } from "@/services/dashboard";
import { getTranslations } from "next-intl/server";

export default async function DashboardPage() {
  const t = await getTranslations("dashboard");
  const summaries = await getDashboardSummaries();

  return (
    <div className="space-y-10">
      <DashboardFeature summaries={summaries} />
    </div>
  );
}
