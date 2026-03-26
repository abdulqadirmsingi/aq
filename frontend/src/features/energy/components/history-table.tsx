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
  marketSegment: "retail" | "wholesale";
}

export async function HistoryTable({ history, query, marketSegment }: HistoryTableProps) {
  const t = await getTranslations();
  const selectedYear =
    marketSegment === "retail" ? query.retailHistoryYear : query.wholesaleHistoryYear;

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
        title={
          marketSegment === "retail"
            ? t("energy.retailHistory")
            : t("energy.wholesaleHistory")
        }
        description={
          selectedYear
            ? t(
                marketSegment === "retail"
                  ? "energy.retailHistoryDescription"
                  : "energy.wholesaleHistoryDescription",
                {
                count: history.meta.total,
                year: selectedYear,
              },
            )
            : t(
                marketSegment === "retail"
                  ? "energy.retailHistoryOnDemandDescription"
                  : "energy.wholesaleHistoryOnDemandDescription",
              )
        }
      />
      <DataTable
        columns={columns}
        data={history.items}
        keyExtractor={(item) => item.id}
        emptyMessage={
          selectedYear
            ? t("common.noData")
            : t(
                marketSegment === "retail"
                  ? "energy.selectRetailHistoryYear"
                  : "energy.selectWholesaleHistoryYear",
              )
        }
      />
      {selectedYear ? (
        <TablePagination
          query={query}
          offsetKey={
            marketSegment === "retail" ? "retailHistoryOffset" : "wholesaleHistoryOffset"
          }
          limit={history.meta.limit}
          offset={history.meta.offset}
          total={history.meta.total}
          hasNext={history.meta.has_next}
        />
      ) : null}
    </div>
  );
}
