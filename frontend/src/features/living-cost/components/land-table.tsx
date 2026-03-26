"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { LandPrice } from "@/types/api";
import { useTranslations } from "next-intl";

interface LandTableProps {
  data: LandPrice[];
}

export function LandTable({ data }: LandTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "location",
      header: t("livingCost.location"),
      render: (item: LandPrice) => <span className="font-medium">{item.location}</span>,
    },
    {
      key: "category",
      header: t("common.category"),
      render: (item: LandPrice) => <Badge>{item.category}</Badge>,
    },
    {
      key: "price",
      header: t("livingCost.pricePerSqm"),
      render: (item: LandPrice) => (
        <span className="font-medium">{formatNumber(item.pricePerSqm)}</span>
      ),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: LandPrice) => {
        const trend = computeTrend(item.pricePerSqm, item.previousPrice);
        const change = computeChangePercent(item.pricePerSqm, item.previousPrice);
        return <TrendIndicator trend={trend} value={change} />;
      },
    },
  ];

  return (
    <div>
      <SectionHeader title={t("livingCost.land")} description={t("livingCost.landDescription")} />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
