import { EnergyFeature } from "@/features/energy";
import { getEnergyPageData } from "@/services/energy";
import type { EnergyQueryState, EnergyTabId } from "@/features/energy/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

interface EnergyPageProps {
  searchParams: SearchParams;
}

function readSingleValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function readInt(value: string | string[] | undefined): number | undefined {
  const raw = readSingleValue(value);
  if (!raw) {
    return undefined;
  }
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : undefined;
}

function readTab(value: string | string[] | undefined): EnergyTabId {
  const raw = readSingleValue(value);
  if (
    raw === "retail"
    || raw === "wholesale"
    || raw === "rollups"
    || raw === "insights"
    || raw === "overview"
  ) {
    return raw;
  }
  return "overview";
}

export default async function EnergyPage({ searchParams }: EnergyPageProps) {
  const params = await searchParams;
  const query: EnergyQueryState = {
    activeTab: readTab(params.tab),
    fuelType: readSingleValue(params.fuelType),
    locationQuery: readSingleValue(params.locationQuery),
    retailHistoryYear: readInt(params.retailHistoryYear),
    wholesaleHistoryYear: readInt(params.wholesaleHistoryYear),
    retailLatestOffset: readInt(params.retailLatestOffset) ?? 0,
    retailHistoryOffset: readInt(params.retailHistoryOffset) ?? 0,
    wholesaleLatestOffset: readInt(params.wholesaleLatestOffset) ?? 0,
    wholesaleHistoryOffset: readInt(params.wholesaleHistoryOffset) ?? 0,
    rollupsOffset: readInt(params.rollupsOffset) ?? 0,
  };
  const data = await getEnergyPageData(query);

  return (
    <>
      <EnergyFeature data={data} />
    </>
  );
}
