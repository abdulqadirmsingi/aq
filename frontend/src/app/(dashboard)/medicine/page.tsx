import type { Metadata } from "next";
import { MedicineFeature } from "@/features/medicine";
import { buildPageMetadata } from "@/lib/seo";
import { getDrugPrices } from "@/services/medicine";

export const metadata: Metadata = buildPageMetadata({
  title: "Medicine Price Watch",
  description:
    "Follow medicine pricing signals and availability patterns through AQ's structured health data view.",
  path: "/medicine",
  imageTitle: "Medicine Price Watch",
  imageDetail: "Structured medicine pricing signals designed for easy sharing and review.",
  keywords: ["medicine prices", "health data", "drug prices", "Tanzania medicine market"],
});

export const revalidate = 86400;

export default async function MedicinePage() {
  const drugPrices = await getDrugPrices();

  return (
    <div className="space-y-10">
      <MedicineFeature drugPrices={drugPrices} />
    </div>
  );
}
