import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import type { EwuraFuelObservationPage, EwuraFuelObservationRead } from "@/types/api";
import { getTranslations } from "next-intl/server";
import { TablePagination } from "./table-pagination";
import type { EnergyQueryState } from "../types";

interface HistoryTableProps {
  history: EwuraFuelObservationPage;
  query: EnergyQueryState;
}

export async function HistoryTable({ history, query }: HistoryTableProps) {
  const t = await getTranslations();

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
        description={
          query.historyYear
            ? t("energy.historyDescription", {
                count: history.meta.total,
                year: query.historyYear,
              })
            : t("energy.historyOnDemandDescription")
        }
      />
      <DataTable
        columns={columns}
        data={history.items}
        keyExtractor={(item) => item.id}
        emptyMessage={
          query.historyYear ? t("common.noData") : t("energy.selectHistoryYear")
        }
      />
      {query.historyYear ? (
        <TablePagination
          query={query}
          offsetKey="historyOffset"
          limit={history.meta.limit}
          offset={history.meta.offset}
          total={history.meta.total}
          hasNext={history.meta.has_next}
        />
      ) : null}
    </div>
  );
}
