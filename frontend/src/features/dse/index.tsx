import type { DsePageData } from "./types";
import { DseSummaryCards } from "./components/dse-summary-cards";
import { DseMarketTable } from "./components/dse-market-table";
import { DseStatsBar } from "./components/dse-stats-bar";

interface DseFeatureProps {
  data: DsePageData;
}

export function DseFeature({ data }: DseFeatureProps) {
  return (
    <div className="space-y-8">
      <DseSummaryCards summary={data.summary} />
      <DseStatsBar summary={data.summary} />
      <DseMarketTable
        items={data.latest.items}
        tradeDate={data.summary.trade_date}
      />
    </div>
  );
}
