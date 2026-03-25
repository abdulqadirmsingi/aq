import { PageHeader } from "@/components/ui/page-header";
import { HrFeature } from "@/features/hr";
import { getJobTrends, getSalaries } from "@/services/hr";
import { getTranslations } from "next-intl/server";

export default async function HrPage() {
  const t = await getTranslations("hr");
  const [salaries, jobTrends] = await Promise.all([getSalaries(), getJobTrends()]);

  return (
    <>
      <PageHeader title={t("title")} subtitle={t("subtitle")} />
      <HrFeature salaries={salaries} jobTrends={jobTrends} />
    </>
  );
}
