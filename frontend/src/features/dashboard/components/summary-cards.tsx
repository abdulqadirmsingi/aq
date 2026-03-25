"use client";

import { DataCard } from "@/components/ui/data-card";
import type { DomainSummary } from "@/types";
import { useTranslations } from "next-intl";

interface SummaryCardsProps {
  summaries: DomainSummary[];
}

export function SummaryCards({ summaries }: SummaryCardsProps) {
  const t = useTranslations();

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      {summaries.map((item) => (
        <DataCard
          key={item.label}
          title={t(item.label)}
          value={item.value}
          change={item.change}
          trend={item.trend}
        />
      ))}
    </div>
  );
}
