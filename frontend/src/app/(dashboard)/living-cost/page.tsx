import { LivingCostFeature } from "@/features/living-cost";
import { getLandPrices, getRentPrices } from "@/services/living-cost";

export default async function LivingCostPage() {
  const [rentPrices, landPrices] = await Promise.all([getRentPrices(), getLandPrices()]);

  return (
    <>
      <LivingCostFeature rentPrices={rentPrices} landPrices={landPrices} />
    </>
  );
}
