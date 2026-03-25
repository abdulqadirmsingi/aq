import { PageHeader } from "@/components/ui/page-header";
import { MedicineFeature } from "@/features/medicine";
import { getDrugPrices } from "@/services/medicine";
import { getTranslations } from "next-intl/server";

export default async function MedicinePage() {
  const t = await getTranslations("medicine");
  const drugPrices = await getDrugPrices();

  return (
    <>
      <PageHeader title={t("title")} subtitle={t("subtitle")} />
      <MedicineFeature drugPrices={drugPrices} />
    </>
  );
}
