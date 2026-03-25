"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import type { EwuraFuelObservationPage, EwuraFuelObservationRead } from "@/types/api";
import { useTranslations } from "next-intl";

interface HistoryTableProps {
  history: EwuraFuelObservationPage;
}

export function HistoryTable({ history }: HistoryTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "month",
      header: t("money.month"),
      render: (item: EwuraFuelObservationRead) => item.month_label,
    },
    {
      key: "fuel",
      header: t("energy.fuelType"),
      render: (item: EwuraFuelObservationRead) => (
        <Badge>{t(`energy.fuelLabels.${item.fuel_type}`)}</Badge>
      ),
    },
    {
      key: "location",
      header: t("energy.location"),
      render: (item: EwuraFuelObservationRead) =>
        item.canonical_location_name ?? item.raw_location_text,
    },
    {
      key: "price",
      header: t("common.price"),
      render: (item: EwuraFuelObservationRead) => item.price_display,
    },
    {
      key: "source",
      header: t("common.source"),
      render: (item: EwuraFuelObservationRead) => item.source_label,
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("energy.history")}
        description={t("energy.historyDescription", { count: history.meta.total })}
      />
      <DataTable
        columns={columns}
        data={history.items}
        keyExtractor={(item) => item.id}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}
