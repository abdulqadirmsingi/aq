import { EnergyFeature } from "@/features/energy";
import { getEnergyPageData } from "@/services/energy";

export default async function EnergyPage() {
  const data = await getEnergyPageData();

  return (
    <>
      <EnergyFeature data={data} />
    </>
  );
}
