import { DashboardFeature } from "@/features/dashboard";
import { getDashboardSummaries } from "@/services/dashboard";

export default async function DashboardPage() {
  const summaries = await getDashboardSummaries();

  return (
    <div className="space-y-10">
      <DashboardFeature summaries={summaries} />
    </div>
  );
}
