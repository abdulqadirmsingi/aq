import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { formatNumber } from "@/lib/utils";
import { getTranslations } from "next-intl/server";
import type { DseStockRead } from "@/types/api";

interface DseMarketTableProps {
  items: DseStockRead[];
  tradeDate: string | null;
}

function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return formatNumber(Math.round(value));
}

function formatTurnover(value: number | null | undefined): string {
  if (!value || value === 0) return "—";
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  return formatNumber(Math.round(value));
}

function changeBadge(change: number | null): React.ReactNode {
  if (change === null || change === undefined) return <Badge>—</Badge>;
  if (change > 0) return <Badge variant="success">+{change.toFixed(2)}%</Badge>;
  if (change < 0) return <Badge variant="danger">{change.toFixed(2)}%</Badge>;
  return <Badge>{change.toFixed(2)}%</Badge>;
}

export async function DseMarketTable({ items, tradeDate }: DseMarketTableProps) {
  const t = await getTranslations();

  const columns = [
    {
      key: "symbol",
      header: t("dse.symbol"),
      render: (item: DseStockRead) => (
        <span className="font-black tracking-tight">{item.symbol}</span>
      ),
    },
    {
      key: "close",
      header: t("dse.close"),
      render: (item: DseStockRead) => formatPrice(item.close_price),
    },
    {
      key: "open",
      header: t("dse.open"),
      render: (item: DseStockRead) => formatPrice(item.open_price),
    },
    {
      key: "high",
      header: t("common.high"),
      render: (item: DseStockRead) => formatPrice(item.high_price),
    },
    {
      key: "low",
      header: t("common.low"),
      render: (item: DseStockRead) => formatPrice(item.low_price),
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: DseStockRead) => changeBadge(item.change_pct),
    },
    {
      key: "turnover",
      header: t("dse.turnover"),
      render: (item: DseStockRead) => (
        <span className={!item.turnover_tzs || item.turnover_tzs === 0 ? "text-neutral-400" : ""}>
          {formatTurnover(item.turnover_tzs)}
        </span>
      ),
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("dse.marketSummary")}
        description={
          tradeDate
            ? t("dse.marketSummaryDescription", { date: tradeDate })
            : t("dse.marketSummaryDescriptionFallback")
        }
      />
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(item) => `${item.symbol}:${item.trade_date}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}
