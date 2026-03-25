"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { FuelPrice } from "@/types/api";
import { useTranslations } from "next-intl";

interface FuelPriceTableProps {
  data: FuelPrice[];
}

const fuelTypeMap: Record<string, string> = {
  petrol: "energy.petrol",
  diesel: "energy.diesel",
  kerosene: "energy.kerosene",
};

export function FuelPriceTable({ data }: FuelPriceTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "fuelType",
      header: t("energy.fuelType"),
      render: (item: FuelPrice) => (
        <Badge>{t(fuelTypeMap[item.fuelType] ?? item.fuelType)}</Badge>
      ),
    },
    {
      key: "region",
      header: t("common.region"),
      render: (item: FuelPrice) => item.region,
    },
    {
      key: "price",
      header: t("energy.pricePerLitre"),
      render: (item: FuelPrice) => (
        <span className="font-medium">{formatNumber(item.pricePerLitre)}</span>
      ),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: FuelPrice) => {
        const trend = computeTrend(item.pricePerLitre, item.previousPrice);
        const change = computeChangePercent(item.pricePerLitre, item.previousPrice);
        return <TrendIndicator trend={trend} value={change} />;
      },
    },
  ];

  return (
    <div>
      <SectionHeader title={t("energy.fuelPrices")} description={t("energy.fuelDescription")} />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
