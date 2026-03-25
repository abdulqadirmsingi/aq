import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import type { EwuraFuelRollupRead } from "@/types/api";
import { getTranslations } from "next-intl/server";

interface RollupsTableProps {
  data: EwuraFuelRollupRead[];
}

export async function RollupsTable({ data }: RollupsTableProps) {
  const t = await getTranslations();

  const columns = [
    {
      key: "group",
      header: t("energy.group"),
      render: (item: EwuraFuelRollupRead) => item.group_name,
    },
    {
      key: "fuel",
      header: t("energy.fuelType"),
      render: (item: EwuraFuelRollupRead) => (
        <Badge>{t(`energy.fuelLabels.${item.fuel_type}`)}</Badge>
      ),
    },
    {
      key: "average",
      header: t("common.average"),
      render: (item: EwuraFuelRollupRead) => item.avg_price_display,
    },
    {
      key: "range",
      header: t("energy.range"),
      render: (item: EwuraFuelRollupRead) =>
        `${item.min_price_display} - ${item.max_price_display}`,
    },
    {
      key: "count",
      header: t("energy.observations"),
      render: (item: EwuraFuelRollupRead) => String(item.observations_count),
    },
  ];

  return (
    <div>
      <SectionHeader title={t("energy.rollups")} description={t("energy.rollupsDescription")} />
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={(item) => `${item.group_name}-${item.fuel_type}-${item.snapshot_date}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}
