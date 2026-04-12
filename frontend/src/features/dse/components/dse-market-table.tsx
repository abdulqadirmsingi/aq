import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { getTranslations } from "next-intl/server";
import type { DseStockRead, DseStockPage } from "@/types/api";

interface DseMarketTableProps {
  page: DseStockPage;
  tradeDate: string | null;
  currentOffset: number;
}

function changeBadge(item: DseStockRead): React.ReactNode {
  if (item.change_direction === "up") {
    return <Badge variant="success">{item.change_pct_display}</Badge>;
  }
  if (item.change_direction === "down") {
    return <Badge variant="danger">{item.change_pct_display}</Badge>;
  }
  return <Badge>{item.change_pct_display}</Badge>;
}

export async function DseMarketTable({ page, tradeDate, currentOffset }: DseMarketTableProps) {
  const t = await getTranslations();

  const { items, meta } = page;
  const prevOffset = Math.max(0, currentOffset - meta.limit);
  const nextOffset = currentOffset + meta.limit;
  const hasPrev = currentOffset > 0;
  const hasNext = meta.has_next;
  const start = meta.total === 0 ? 0 : currentOffset + 1;
  const end = Math.min(currentOffset + items.length, meta.total);

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
      render: (item: DseStockRead) => item.close_price_display,
    },
    {
      key: "open",
      header: t("dse.open"),
      render: (item: DseStockRead) => item.open_price_display,
    },
    {
      key: "high",
      header: t("common.high"),
      render: (item: DseStockRead) => item.high_price_display,
    },
    {
      key: "low",
      header: t("common.low"),
      render: (item: DseStockRead) => item.low_price_display,
    },
    {
      key: "change",
      header: t("common.change"),
      render: (item: DseStockRead) => changeBadge(item),
    },
    {
      key: "turnover",
      header: t("dse.turnover"),
      render: (item: DseStockRead) => item.turnover_display,
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

      {meta.total > meta.limit && (
        <div className="mt-4 flex items-center justify-between border-[3px] border-neutral-950 bg-white px-6 py-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <span className="text-xs font-bold text-neutral-500">
            {t("dse.paginationSummary", { start, end, total: meta.total })}
          </span>
          <div className="flex gap-2">
            {hasPrev ? (
              <a
                href={`?offset=${prevOffset}`}
                className="border-[2px] border-neutral-950 bg-white px-4 py-1.5 text-xs font-black uppercase tracking-widest shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] transition-all hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
              >
                {t("common.previous")}
              </a>
            ) : (
              <span className="border-[2px] border-neutral-300 px-4 py-1.5 text-xs font-black uppercase tracking-widest text-neutral-300">
                {t("common.previous")}
              </span>
            )}
            {hasNext ? (
              <a
                href={`?offset=${nextOffset}`}
                className="border-[2px] border-neutral-950 bg-neutral-950 px-4 py-1.5 text-xs font-black uppercase tracking-widest text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] transition-all hover:translate-x-[1px] hover:translate-y-[1px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
              >
                {t("common.next")}
              </a>
            ) : (
              <span className="border-[2px] border-neutral-300 px-4 py-1.5 text-xs font-black uppercase tracking-widest text-neutral-300">
                {t("common.next")}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
