"use client";

import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { RentPrice } from "@/types/api";
import { useTranslations } from "next-intl";

interface RentTableProps {
  data: RentPrice[];
}

export function RentTable({ data }: RentTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "area",
      header: t("livingCost.area"),
      render: (item: RentPrice) => <span className="font-medium">{item.area}</span>,
    },
    {
      key: "type",
      header: t("livingCost.propertyType"),
      render: (item: RentPrice) => item.propertyType,
    },
    {
      key: "bedrooms",
      header: t("livingCost.bedrooms"),
      render: (item: RentPrice) => item.bedrooms,
    },
    {
      key: "rent",
      header: t("livingCost.monthlyRent"),
      render: (item: RentPrice) => (
        <span className="font-medium">{formatNumber(item.monthlyRent)}</span>
      ),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: RentPrice) => {
        const trend = computeTrend(item.monthlyRent, item.previousRent);
        const change = computeChangePercent(item.monthlyRent, item.previousRent);
        return <TrendIndicator trend={trend} value={change} />;
      },
    },
  ];

  return (
    <div>
      <SectionHeader title={t("livingCost.rent")} description={t("livingCost.rentDescription")} />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
