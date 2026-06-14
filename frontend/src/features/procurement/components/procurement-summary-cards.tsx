import { DataCard } from "@/components/ui/data-card";
import { getTranslations } from "next-intl/server";
import type { TenderFiltersRead } from "@/types/api";

interface ProcurementSummaryCardsProps {
  filters: TenderFiltersRead;
  total: number;
}

export async function ProcurementSummaryCards({ filters, total }: ProcurementSummaryCardsProps) {
  const t = await getTranslations();

  const cards = [
    {
      key: "total",
      title: t("procurement.totalTenders"),
      value: total.toLocaleString(),
      subtitle: t("procurement.tendersDescription", { count: total, total }),
      variant: "featured" as const,
    },
    {
      key: "published",
      title: t("procurement.totalPublished"),
      value: filters.total_published.toLocaleString(),
      subtitle: "tender_status = active",
    },
    {
      key: "awarded",
      title: t("procurement.totalAwarded"),
      value: filters.total_awarded.toLocaleString(),
      subtitle: "has_award = true",
    },
    {
      key: "entities",
      title: t("procurement.procuringEntities"),
      value: filters.procuring_entities.length.toLocaleString(),
      subtitle: "NeST PPRA · OCDS data",
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
