import type { DsePageData } from "./types";
import { DseSummaryCards } from "./components/dse-summary-cards";
import { DseMarketTable } from "./components/dse-market-table";
import { DseStatsBar } from "./components/dse-stats-bar";

interface DseFeatureProps {
  data: DsePageData;
  offset: number;
}

export function DseFeature({ data, offset }: DseFeatureProps) {
  return (
    <div className="space-y-8">
      <DseSummaryCards summary={data.summary} />
      <DseStatsBar summary={data.summary} />
      <DseMarketTable
        page={data.latest}
        tradeDate={data.summary.trade_date}
        currentOffset={offset}
      />
    </div>
  );
}
