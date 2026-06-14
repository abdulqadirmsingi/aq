import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { getTranslations } from "next-intl/server";
import type { TenderPage, TenderRead } from "@/types/api";

interface TenderTableProps {
  page: TenderPage;
  currentOffset: number;
}

function statusBadge(tender: TenderRead): React.ReactNode {
  if (tender.has_award) {
    return <Badge variant="success">{tender.contractor_name ?? "Awarded"}</Badge>;
  }
  switch (tender.tender_status) {
    case "active":
      return <Badge variant="success">Active</Badge>;
    case "complete":
      return <Badge>Complete</Badge>;
    case "cancelled":
      return <Badge variant="danger">Cancelled</Badge>;
    default:
      return <Badge>{tender.tender_status ?? "—"}</Badge>;
  }
}

function formatAmount(amount: string | null, currency: string | null): string {
  if (!amount) return "—";
  const num = parseFloat(amount);
  if (isNaN(num)) return "—";
  const formatted =
    num >= 1_000_000
      ? `${(num / 1_000_000).toFixed(1)}M`
      : num >= 1_000
        ? `${(num / 1_000).toFixed(0)}K`
        : num.toFixed(0);
  return `${formatted} ${currency ?? "TZS"}`;
}

export async function TenderTable({ page, currentOffset }: TenderTableProps) {
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
      key: "reference",
      header: t("procurement.reference"),
      render: (item: TenderRead) => (
        <span className="font-mono text-xs font-bold tracking-tight text-neutral-600">
          {item.tender_reference}
        </span>
      ),
    },
    {
      key: "entity",
      header: t("procurement.entity"),
      render: (item: TenderRead) => (
        <span className="max-w-[180px] truncate block text-sm font-semibold">
          {item.procuring_entity_name ?? "—"}
        </span>
      ),
    },
    {
      key: "description",
      header: "Description",
      render: (item: TenderRead) => (
        <span className="max-w-[240px] truncate block text-xs text-neutral-600">
          {item.description ?? item.title ?? t("procurement.noDescription")}
        </span>
      ),
    },
    {
      key: "method",
      header: t("procurement.method"),
      render: (item: TenderRead) => (
        <span className="text-xs text-neutral-500">
          {item.procurement_method_details ?? item.procurement_method ?? "—"}
        </span>
      ),
    },
    {
      key: "award",
      header: t("procurement.awardValue"),
      render: (item: TenderRead) => (
        <span className="font-bold text-sm">
          {formatAmount(item.award_value_amount, item.award_value_currency)}
        </span>
      ),
    },
    {
      key: "status",
      header: t("procurement.status"),
      render: (item: TenderRead) => statusBadge(item),
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("procurement.tenders")}
        description={t("procurement.tendersDescription", {
          count: items.length,
          total: meta.total,
        })}
      />
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(item) => item.id}
        emptyMessage={t("common.noData")}
      />

      {meta.total > meta.limit && (
        <div className="mt-4 flex items-center justify-between border-[3px] border-neutral-950 bg-white px-6 py-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <span className="text-xs font-bold text-neutral-500">
            {t("procurement.paginationSummary", { start, end, total: meta.total })}
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
