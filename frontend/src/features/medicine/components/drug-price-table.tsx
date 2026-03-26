"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { formatNumber } from "@/lib/utils";
import type { DrugPrice } from "@/types/api";
import { useTranslations } from "next-intl";

interface DrugPriceTableProps {
  data: DrugPrice[];
}

const availabilityVariant = {
  available: "success",
  limited: "warning",
  scarce: "danger",
} as const;

export function DrugPriceTable({ data }: DrugPriceTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "name",
      header: t("medicine.drugName"),
      render: (item: DrugPrice) => <span className="font-medium">{item.drugName}</span>,
    },
    {
      key: "generic",
      header: t("medicine.genericName"),
      render: (item: DrugPrice) => (
        <span className="text-neutral-500">{item.genericName}</span>
      ),
    },
    {
      key: "dosage",
      header: t("medicine.dosage"),
      render: (item: DrugPrice) => item.dosage,
    },
    {
      key: "price",
      header: t("medicine.priceRange"),
      render: (item: DrugPrice) => (
        <span className="font-medium">
          {formatNumber(item.minPrice)} – {formatNumber(item.maxPrice)}
        </span>
      ),
    },
    {
      key: "availability",
      header: t("medicine.availability"),
      render: (item: DrugPrice) => (
        <Badge variant={availabilityVariant[item.availability]}>
          {t(`medicine.${item.availability}`)}
        </Badge>
      ),
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("medicine.drugPrices")}
        description={t("medicine.drugDescription")}
      />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
