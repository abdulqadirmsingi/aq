import { MedicineFeature } from "@/features/medicine";
import { getDrugPrices } from "@/services/medicine";

export default async function MedicinePage() {
  const drugPrices = await getDrugPrices();

  return (
    <div className="space-y-10">
      <MedicineFeature drugPrices={drugPrices} />
    </div>
  );
}
