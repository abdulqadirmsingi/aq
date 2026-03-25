"use client";

import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { GasPrice } from "@/types/api";
import { useTranslations } from "next-intl";

interface GasPriceTableProps {
  data: GasPrice[];
}

export function GasPriceTable({ data }: GasPriceTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "gasType",
      header: t("energy.gasType"),
      render: (item: GasPrice) => item.gasType,
    },
    {
      key: "weight",
      header: t("energy.weight"),
      render: (item: GasPrice) => item.weight,
    },
    {
      key: "price",
      header: t("common.price") + " (TZS)",
      render: (item: GasPrice) => (
        <span className="font-medium">{formatNumber(item.price)}</span>
      ),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: GasPrice) => {
        const trend = computeTrend(item.price, item.previousPrice);
        const change = computeChangePercent(item.price, item.previousPrice);
        return <TrendIndicator trend={trend} value={change} />;
      },
    },
  ];

  return (
    <div>
      <SectionHeader title={t("energy.gasPrices")} description={t("energy.gasDescription")} />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
