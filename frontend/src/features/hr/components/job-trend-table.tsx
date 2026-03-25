"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { formatNumber } from "@/lib/utils";
import type { JobTrend } from "@/types/api";
import { useTranslations } from "next-intl";

interface JobTrendTableProps {
  data: JobTrend[];
}

const demandVariant = {
  growing: "success",
  stable: "default",
  declining: "danger",
} as const;

const demandTrend = {
  growing: "up",
  stable: "stable",
  declining: "down",
} as const;

export function JobTrendTable({ data }: JobTrendTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "role",
      header: t("hr.role"),
      render: (item: JobTrend) => <span className="font-medium">{item.role}</span>,
    },
    {
      key: "sector",
      header: t("hr.sector"),
      render: (item: JobTrend) => <Badge>{item.sector}</Badge>,
    },
    {
      key: "demand",
      header: t("hr.demand"),
      render: (item: JobTrend) => (
        <Badge variant={demandVariant[item.demand]}>{t(`hr.${item.demand}`)}</Badge>
      ),
    },
    {
      key: "openings",
      header: t("hr.openings"),
      render: (item: JobTrend) => formatNumber(item.openings),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: JobTrend) => (
        <TrendIndicator trend={demandTrend[item.demand]} value={item.changePercent} />
      ),
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("hr.jobTrends")}
        description={t("hr.jobTrendsDescription")}
      />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
