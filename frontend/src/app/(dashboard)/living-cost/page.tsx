import type { Metadata } from "next";
import { LivingCostFeature } from "@/features/living-cost";
import { buildPageMetadata } from "@/lib/seo";
import { getLandPrices, getRentPrices } from "@/services/living-cost";

export const metadata: Metadata = buildPageMetadata({
  title: "Living Cost Signals",
  description:
    "See rent and land pricing signals in a structured dashboard built for regional market context.",
  path: "/living-cost",
  imageTitle: "Living Cost Signals",
  imageDetail: "Rent and land price indicators in one structured AQ view.",
  keywords: ["living cost", "rent prices", "land prices", "Tanzania housing data"],
});

export default async function LivingCostPage() {
  const [rentPrices, landPrices] = await Promise.all([getRentPrices(), getLandPrices()]);

  return (
    <>
      <LivingCostFeature rentPrices={rentPrices} landPrices={landPrices} />
    </>
  );
}
