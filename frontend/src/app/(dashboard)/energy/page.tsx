import type { Metadata } from "next";
import { EnergyFeature } from "@/features/energy";
import { getEnergyPageData } from "@/services/energy";
import type { EnergyQueryState, EnergyTabId } from "@/features/energy/types";
import { buildPageMetadata, readQueryValue } from "@/lib/seo";

export const revalidate = 3600;

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

export async function generateMetadata({
  searchParams,
}: EnergyPageProps): Promise<Metadata> {
  const params = await searchParams;
  const fuelType = readQueryValue(params.fuelType);
  const locationQuery = readQueryValue(params.locationQuery);
  const tab = readTab(params.tab);

  const titleParts = ["Energy Data"];
  if (fuelType) {
    titleParts.unshift(`${fuelType.toUpperCase()} Prices`);
  }

  const locationLabel = locationQuery ? ` for ${locationQuery}` : "";
  const tabLabel = tab === "overview" ? "overview" : tab.replaceAll("-", " ");
  const detail = `${tabLabel} of EWURA fuel data${locationLabel}`.replace(/^./, (letter) =>
    letter.toUpperCase(),
  );

  return buildPageMetadata({
    title: titleParts.join(" "),
    description: `Track regulated fuel pricing, history, and rollups${locationLabel} from AQ's energy data workspace.`,
    path: "/energy",
    query: params,
    imageTitle: titleParts.join(" "),
    imageDetail: detail,
    keywords: ["energy data", "EWURA fuel prices", "Tanzania fuel dashboard"],
  });
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
