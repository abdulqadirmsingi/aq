import { EnergySummaryCards } from "./components/energy-summary-cards";
import { EnergyFiltersBar } from "./components/energy-filters-bar";
import { EnergyTabs } from "./components/energy-tabs";
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
      <EnergyTabs query={data.query} />
      <EnergyFiltersBar filters={data.filters} query={data.query} />
      {data.query.activeTab === "overview" ? (
        <TrendsTable data={data.currentYearTrends} />
      ) : null}
      {data.query.activeTab === "retail" ? (
        <>
          <LatestPricesTable
            data={data.retailLatestPrices}
            query={data.query}
            marketSegment="retail"
          />
          <HistoryTable history={data.retailHistory} query={data.query} marketSegment="retail" />
        </>
      ) : null}
      {data.query.activeTab === "wholesale" ? (
        <>
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
        </>
      ) : null}
      {data.query.activeTab === "rollups" ? (
        <RollupsTable data={data.rollups} query={data.query} />
      ) : null}
      {data.query.activeTab === "insights" ? (
        <InsightsPanel insights={data.insights} />
      ) : null}
    </div>
  );
}
