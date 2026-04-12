import { DataCard } from "@/components/ui/data-card";
import { getTranslations } from "next-intl/server";
import type { DseDashboardSummaryRead } from "@/types/api";

interface DseSummaryCardsProps {
  summary: DseDashboardSummaryRead;
}

export async function DseSummaryCards({ summary }: DseSummaryCardsProps) {
  const t = await getTranslations();

  const cards = [
    {
      key: "top-gainer",
      title: t("dse.topGainer"),
      value: summary.top_gainer?.symbol ?? "N/A",
      subtitle: summary.top_gainer
        ? `${summary.top_gainer.change_pct_display} · ${summary.top_gainer.close_price_display} TZS`
        : t("common.noData"),
      variant: "featured" as const,
    },
    {
      key: "top-loser",
      title: t("dse.topLoser"),
      value: summary.top_loser?.symbol ?? "N/A",
      subtitle: summary.top_loser
        ? `${summary.top_loser.change_pct_display} · ${summary.top_loser.close_price_display} TZS`
        : t("common.noData"),
    },
    {
      key: "most-traded",
      title: t("dse.mostTraded"),
      value: summary.most_traded?.symbol ?? "N/A",
      subtitle: summary.most_traded
        ? summary.most_traded.turnover_display
        : t("common.noData"),
    },
    {
      key: "total-turnover",
      title: t("dse.totalTurnover"),
      value: summary.total_turnover_display,
      subtitle: summary.trade_date
        ? `${t("dse.tradeDate")}: ${summary.trade_date}`
        : t("common.noData"),
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
          variant={card.variant ?? "default"}
          className={index === 0 ? "sm:col-span-2" : undefined}
        />
      ))}
    </div>
  );
}
