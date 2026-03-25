"use client";

import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { computeChangePercent, computeTrend } from "@/lib/utils";
import type { InflationRecord } from "@/types/api";
import { useTranslations } from "next-intl";

interface InflationTableProps {
  data: InflationRecord[];
}

export function InflationTable({ data }: InflationTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "month",
      header: t("money.month"),
      render: (item: InflationRecord) => (
        <span className="font-medium">{item.month}</span>
      ),
    },
    {
      key: "rate",
      header: t("money.rate"),
      render: (item: InflationRecord) => `${item.rate}%`,
    },
    {
      key: "yoy",
      header: t("money.yearOverYear"),
      render: (item: InflationRecord) => `${item.yearOverYear}%`,
    },
    {
      key: "change",
      header: t("common.trend"),
      render: (item: InflationRecord) => {
        const trend = computeTrend(item.rate, item.previousRate);
        const change = computeChangePercent(item.rate, item.previousRate);
        return <TrendIndicator trend={trend} value={change} />;
      },
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("money.inflation")}
        description={t("money.inflationDescription")}
      />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
