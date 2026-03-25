"use client";

import { DataCard } from "@/components/ui/data-card";
import type { EwuraFuelLatestExtremesRead, EwuraFuelLatestSummaryRead } from "@/types/api";
import { useTranslations } from "next-intl";

interface EnergySummaryCardsProps {
  summary: EwuraFuelLatestSummaryRead | null;
  latestExtremes: EwuraFuelLatestExtremesRead | null;
  monthsCount: number;
}

export function EnergySummaryCards({
  summary,
  latestExtremes,
  monthsCount,
}: EnergySummaryCardsProps) {
  const t = useTranslations();

  if (!summary) {
    return null;
  }

  const cards = summary.items.map((item) => ({
    key: item.fuel_type,
    title: t(`energy.fuelLabels.${item.fuel_type}`),
    value: item.avg_price_display,
    subtitle: `${t("energy.range")}: ${item.min_price_display} - ${item.max_price_display}`,
  }));

  if (latestExtremes?.cheapest[0] && latestExtremes?.most_expensive[0]) {
    cards.push({
      key: "coverage",
      title: t("energy.marketCoverage"),
      value: String(monthsCount),
      subtitle: `${t("energy.cheapest")}: ${latestExtremes.cheapest[0].price_display} · ${t("energy.highest")}: ${latestExtremes.most_expensive[0].price_display}`,
    });
  }

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
