import { EnergySummaryCards } from "./components/energy-summary-cards";
import { EnergyFiltersBar } from "./components/energy-filters-bar";
import { HistoryTable } from "./components/history-table";
import { InsightsPanel } from "./components/insights-panel";
import { LatestPricesTable } from "./components/latest-prices-table";
import { RollupsTable } from "./components/rollups-table";
import { TrendsTable } from "./components/trends-table";
import type { EnergyPageData } from "./types";

interface EnergyFeatureProps {
  data: EnergyPageData;
}

export function EnergyFeature({ data }: EnergyFeatureProps) {
  return (
    <div className="space-y-8">
      <EnergySummaryCards
        summary={data.dashboardSummary.latest_summary}
        latestExtremes={data.latestExtremes}
        monthsCount={data.availableMonths.length}
      />
      <EnergyFiltersBar filters={data.filters} query={data.query} />
      <LatestPricesTable
        data={data.retailLatestPrices}
        query={data.query}
        marketSegment="retail"
      />
      <TrendsTable data={data.currentYearTrends} />
      <HistoryTable history={data.retailHistory} query={data.query} marketSegment="retail" />
      <LatestPricesTable
        data={data.wholesaleLatestPrices}
        query={data.query}
        marketSegment="wholesale"
      />
      <HistoryTable
        history={data.wholesaleHistory}
        query={data.query}
        marketSegment="wholesale"
      />
      <RollupsTable data={data.rollups} />
      <InsightsPanel insights={data.insights} />
    </div>
  );
}
