import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import type { EwuraFuelLatestPriceRead } from "@/types/api";
import { getTranslations } from "next-intl/server";

interface LatestPricesTableProps {
  data: EwuraFuelLatestPriceRead[];
}

export async function LatestPricesTable({ data }: LatestPricesTableProps) {
  const t = await getTranslations();

  const columns = [
    {
      key: "fuel",
      header: t("energy.fuelType"),
      render: (item: EwuraFuelLatestPriceRead) => (
        <Badge>{t(`energy.fuelLabels.${item.fuel_type}`)}</Badge>
      ),
    },
    {
      key: "location",
      header: t("energy.location"),
      render: (item: EwuraFuelLatestPriceRead) =>
        item.canonical_location_name ?? item.raw_location_text,
    },
    {
      key: "month",
      header: t("money.month"),
      render: (item: EwuraFuelLatestPriceRead) => item.snapshot_month_label,
    },
    {
      key: "price",
      header: t("common.price"),
      render: (item: EwuraFuelLatestPriceRead) => (
        <span className="font-medium">{item.price_display}</span>
      ),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: EwuraFuelLatestPriceRead) =>
        item.percent_change === null ? (
          <span className="text-neutral-400">{t("energy.noPreviousComparison")}</span>
        ) : (
          <TrendIndicator
            trend={
              item.percent_change > 0 ? "up" : item.percent_change < 0 ? "down" : "stable"
            }
            value={item.percent_change}
          />
        ),
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("energy.latestPrices")}
        description={t("energy.latestPricesDescription")}
      />
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={(item) => `${item.fuel_type}-${item.raw_location_text}-${item.snapshot_date}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}
