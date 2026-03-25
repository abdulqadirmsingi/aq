import { PageHeader } from "@/components/ui/page-header";
import type { MoneyPageData } from "./types";
import { getTranslations } from "next-intl/server";
import { BotHistoryTable, ComparisonTable, GapTable, OpportunityTable, RecommendationPanel, SpreadTable, StalenessTable } from "./components/money-sections";
import { MoneyFiltersBar } from "./components/money-filters-bar";
import { MoneySummaryCards } from "./components/money-summary-cards";

interface MoneyFeatureProps {
  data: MoneyPageData;
}

export async function MoneyFeature({ data }: MoneyFeatureProps) {
  const t = await getTranslations();

  return (
    <div className="space-y-8">
      <PageHeader
        title={t("money.title")}
        subtitle={t("money.liveSubtitle", {
          instrument: data.query.instrumentCode,
        })}
      />

      <MoneySummaryCards data={data} />

      <div className="border-[3px] border-neutral-950 bg-white p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        <MoneyFiltersBar
          instrumentCodes={data.filters.instrument_codes}
          query={data.query}
        />
      </div>

      <RecommendationPanel recommendation={data.recommendation} />
      <ComparisonTable items={data.comparison.items} />
      <SpreadTable items={data.spreads.items} />
      <GapTable items={data.benchmarkGaps.items} />
      <OpportunityTable items={data.opportunities.opportunities} />
      <StalenessTable items={data.staleness.items} />
      <BotHistoryTable history={data.botHistory} query={data.query} />
    </div>
  );
}
