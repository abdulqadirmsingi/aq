"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import type { EwuraFuelMonthlyTrendRead } from "@/types/api";
import { useTranslations } from "next-intl";

interface TrendsTableProps {
  data: EwuraFuelMonthlyTrendRead[];
}

export function TrendsTable({ data }: TrendsTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "month",
      header: t("money.month"),
      render: (item: EwuraFuelMonthlyTrendRead) => item.month_label,
    },
    {
      key: "fuel",
      header: t("energy.fuelType"),
      render: (item: EwuraFuelMonthlyTrendRead) => (
        <Badge>{t(`energy.fuelLabels.${item.fuel_type}`)}</Badge>
      ),
    },
    {
      key: "average",
      header: t("common.average"),
      render: (item: EwuraFuelMonthlyTrendRead) => item.avg_price_display,
    },
    {
      key: "range",
      header: t("energy.range"),
      render: (item: EwuraFuelMonthlyTrendRead) =>
        `${item.min_price_display} - ${item.max_price_display}`,
    },
    {
      key: "locations",
      header: t("energy.locations"),
      render: (item: EwuraFuelMonthlyTrendRead) => String(item.locations_count),
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("energy.currentYearTrends")}
        description={t("energy.currentYearTrendsDescription")}
      />
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={(item) => `${item.fuel_type}-${item.month_start}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}
