"use client";

import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { computeChangePercent, computeTrend, formatNumber } from "@/lib/utils";
import type { ExchangeRate } from "@/types/api";
import { useTranslations } from "next-intl";

interface ExchangeRateTableProps {
  data: ExchangeRate[];
}

export function ExchangeRateTable({ data }: ExchangeRateTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "pair",
      header: t("money.currencyPair"),
      render: (item: ExchangeRate) => (
        <span className="font-medium">{item.currencyPair}</span>
      ),
    },
    {
      key: "buy",
      header: t("money.buyRate"),
      render: (item: ExchangeRate) => formatNumber(item.buyRate),
    },
    {
      key: "sell",
      header: t("money.sellRate"),
      render: (item: ExchangeRate) => formatNumber(item.sellRate),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: ExchangeRate) => {
        const trend = computeTrend(item.buyRate, item.previousBuyRate);
        const change = computeChangePercent(item.buyRate, item.previousBuyRate);
        return <TrendIndicator trend={trend} value={change} />;
      },
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("money.exchangeRates")}
        description={t("money.exchangeDescription")}
      />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
