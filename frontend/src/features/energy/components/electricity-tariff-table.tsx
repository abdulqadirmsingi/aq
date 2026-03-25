"use client";

import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { ElectricityTariff } from "@/types/api";
import { useTranslations } from "next-intl";

interface ElectricityTariffTableProps {
  data: ElectricityTariff[];
}

export function ElectricityTariffTable({ data }: ElectricityTariffTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "category",
      header: t("energy.tariffCategory"),
      render: (item: ElectricityTariff) => (
        <span className="font-medium">{item.category}</span>
      ),
    },
    {
      key: "description",
      header: t("common.category"),
      render: (item: ElectricityTariff) => (
        <span className="text-neutral-500">{item.description}</span>
      ),
    },
    {
      key: "rate",
      header: t("energy.ratePerKwh"),
      render: (item: ElectricityTariff) => (
        <span className="font-medium">{formatNumber(item.ratePerKwh)}</span>
      ),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: ElectricityTariff) => {
        const trend = computeTrend(item.ratePerKwh, item.previousRate);
        const change = computeChangePercent(item.ratePerKwh, item.previousRate);
        return <TrendIndicator trend={trend} value={change} />;
      },
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("energy.electricity")}
        description={t("energy.electricityDescription")}
      />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
