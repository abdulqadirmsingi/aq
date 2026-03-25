import { DataCard } from "@/components/ui/data-card";
import { formatNumber } from "@/lib/utils";
import type { MoneyPageData } from "../types";
import { getTranslations } from "next-intl/server";

interface MoneySummaryCardsProps {
  data: MoneyPageData;
}

function formatRate(value: number | null | undefined): string {
  return value === null || value === undefined ? "N/A" : `${formatNumber(Math.round(value))} TZS`;
}

export async function MoneySummaryCards({ data }: MoneySummaryCardsProps) {
  const t = await getTranslations();
  const bestBuy = data.bestRates.buy_forex.best_option;
  const bestSell = data.bestRates.sell_forex.best_option;
  const freshest = data.staleness.items.find((item) => item.is_freshest) ?? data.staleness.items[0];
  const coverage = data.filters.available_months.length;

  const cards = [
    {
      key: "best-buy",
      title: t("money.bestPlaceToBuy"),
      value: bestBuy ? bestBuy.source_name : "N/A",
      subtitle: bestBuy ? `${t("money.rateLabel")}: ${formatRate(bestBuy.relevant_rate)}` : t("common.noData"),
    },
    {
      key: "best-sell",
      title: t("money.bestPlaceToSell"),
      value: bestSell ? bestSell.source_name : "N/A",
      subtitle: bestSell ? `${t("money.rateLabel")}: ${formatRate(bestSell.relevant_rate)}` : t("common.noData"),
    },
    {
      key: "freshest-source",
      title: t("money.freshestSource"),
      value: freshest ? freshest.source_name : "N/A",
      subtitle: freshest?.source_last_updated_at ?? freshest?.data_timestamp ?? t("common.noData"),
    },
    {
      key: "coverage",
      title: t("money.historyCoverage"),
      value: String(coverage),
      subtitle: t("money.historyCoverageDescription"),
    },
  ];

  return (
    <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card, index) => (
        <DataCard
          key={card.key}
          title={card.title}
          value={card.value}
          subtitle={card.subtitle}
          variant={index === 0 ? "featured" : "default"}
          className={index === 0 ? "sm:col-span-2" : undefined}
        />
      ))}
    </div>
  );
}
