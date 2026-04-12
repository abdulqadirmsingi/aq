import { DataCard } from "@/components/ui/data-card";
import { formatNumber } from "@/lib/utils";
import { getTranslations } from "next-intl/server";
import type { DseDashboardSummaryRead } from "@/types/api";

interface DseSummaryCardsProps {
  summary: DseDashboardSummaryRead;
}

function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined) return "N/A";
  return `${formatNumber(Math.round(value))} TZS`;
}

function formatTurnover(value: number): string {
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)}B TZS`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M TZS`;
  return `${formatNumber(Math.round(value))} TZS`;
}

export async function DseSummaryCards({ summary }: DseSummaryCardsProps) {
  const t = await getTranslations();

  const cards = [
    {
      key: "top-gainer",
      title: t("dse.topGainer"),
      value: summary.top_gainer?.symbol ?? "N/A",
      subtitle: summary.top_gainer
        ? `+${summary.top_gainer.change_pct?.toFixed(2) ?? "0"}% · ${formatPrice(summary.top_gainer.close_price)}`
        : t("common.noData"),
      variant: "featured" as const,
    },
    {
      key: "top-loser",
      title: t("dse.topLoser"),
      value: summary.top_loser?.symbol ?? "N/A",
      subtitle: summary.top_loser
        ? `${summary.top_loser.change_pct?.toFixed(2) ?? "0"}% · ${formatPrice(summary.top_loser.close_price)}`
        : t("common.noData"),
    },
    {
      key: "most-traded",
      title: t("dse.mostTraded"),
      value: summary.most_traded?.symbol ?? "N/A",
      subtitle: summary.most_traded?.turnover_tzs
        ? formatTurnover(summary.most_traded.turnover_tzs)
        : t("common.noData"),
    },
    {
      key: "total-turnover",
      title: t("dse.totalTurnover"),
      value: formatTurnover(summary.total_turnover),
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
