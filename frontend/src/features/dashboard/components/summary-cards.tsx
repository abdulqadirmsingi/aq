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
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 auto-rows-[minmax(180px,auto)]">
      {summaries.map((item, index) => {
        // Bento layout rules based on index
        const isHero = index === 0;
        const isSecondaryHero = index === 1;
        const isFeatured = isHero || isSecondaryHero;
        
        return (
          <DataCard
            key={item.label}
            title={t(item.label)}
            value={item.value}
            change={item.change}
            trend={item.trend}
            subtitle={item.subtitle}
            variant={isFeatured ? "featured" : "default"}
            className={
              isHero 
                ? "col-span-1 sm:col-span-2 lg:col-span-2 xl:col-span-3 row-span-2" // Biggest block
                : isSecondaryHero 
                ? "col-span-1 sm:col-span-2 lg:col-span-2 xl:col-span-3 row-span-1" // Wide but shorter
                : "col-span-1 sm:col-span-1 lg:col-span-1 xl:col-span-2 row-span-1"   // Standard small box
            }
          />
        );
      })}
    </div>
  );
}
