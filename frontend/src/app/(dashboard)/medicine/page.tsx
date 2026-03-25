import { MedicineFeature } from "@/features/medicine";
import { getDrugPrices } from "@/services/medicine";
import { getTranslations } from "next-intl/server";

export default async function MedicinePage() {
  const t = await getTranslations("medicine");
  const drugPrices = await getDrugPrices();

  return (
    <div className="space-y-10">
      <MedicineFeature drugPrices={drugPrices} />
    </div>
  );
}
