import { PageHeader } from "@/components/ui/page-header";
import { LivingCostFeature } from "@/features/living-cost";
import { getLandPrices, getRentPrices } from "@/services/living-cost";
import { getTranslations } from "next-intl/server";

export default async function LivingCostPage() {
  const t = await getTranslations("livingCost");
  const [rentPrices, landPrices] = await Promise.all([getRentPrices(), getLandPrices()]);

  return (
    <>
      <PageHeader title={t("title")} subtitle={t("subtitle")} />
      <LivingCostFeature rentPrices={rentPrices} landPrices={landPrices} />
    </>
  );
}
