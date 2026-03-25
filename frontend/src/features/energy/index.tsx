import { EnergySummaryCards } from "./components/energy-summary-cards";
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
      <LatestPricesTable data={data.latestPrices} />
      <TrendsTable data={data.currentYearTrends} />
      <HistoryTable history={data.history} />
      <RollupsTable data={data.rollups} />
      <InsightsPanel insights={data.insights} />
    </div>
  );
}
