import Link from "next/link";
import { getTranslations } from "next-intl/server";
import { buildEnergyHref } from "../query";
import type { EnergyQueryState, EnergyTabId } from "../types";

interface EnergyTabsProps {
  query: EnergyQueryState;
}

const TAB_ORDER: EnergyTabId[] = ["overview", "retail", "wholesale", "rollups", "insights"];

export async function EnergyTabs({ query }: EnergyTabsProps) {
  const t = await getTranslations();

  return (
    <div
      role="tablist"
      aria-label={t("energy.tabsLabel")}
      className="flex flex-wrap gap-3"
    >
      {TAB_ORDER.map((tabId) => {
        const isActive = query.activeTab === tabId;
        return (
          <Link
            key={tabId}
            href={buildEnergyHref(_tabQuery(tabId, query), query)}
            aria-selected={isActive}
            scroll={false}
            className={
              isActive
                ? "border-[3px] border-neutral-950 bg-neutral-950 px-4 py-3 text-xs font-black uppercase tracking-[0.14em] text-white"
                : "border-[3px] border-neutral-950 bg-white px-4 py-3 text-xs font-black uppercase tracking-[0.14em] text-neutral-950"
            }
          >
            {t(`energy.tabs.${tabId}`)}
          </Link>
        );
      })}
    </div>
  );
}

function _tabQuery(tabId: EnergyTabId, query: EnergyQueryState): Partial<EnergyQueryState> {
  const next: Partial<EnergyQueryState> = {
    activeTab: tabId,
    retailLatestOffset: 0,
    retailHistoryOffset: 0,
    wholesaleLatestOffset: 0,
    wholesaleHistoryOffset: 0,
    rollupsOffset: 0,
  };

  if (tabId !== "retail") {
    next.retailHistoryYear = undefined;
  }
  if (tabId !== "wholesale") {
    next.wholesaleHistoryYear = undefined;
  }
  if (tabId === "retail") {
    next.wholesaleHistoryYear = undefined;
  }
  if (tabId === "wholesale") {
    next.retailHistoryYear = undefined;
  }

  return {
    ...query,
    ...next,
  };
}
