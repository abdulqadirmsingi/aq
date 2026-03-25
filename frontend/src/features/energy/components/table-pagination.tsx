import Link from "next/link";
import { getTranslations } from "next-intl/server";
import { buildEnergyHref } from "../query";
import type { EnergyQueryState } from "../types";

interface TablePaginationProps {
  query: EnergyQueryState;
  offsetKey:
    | "retailLatestOffset"
    | "retailHistoryOffset"
    | "wholesaleLatestOffset"
    | "wholesaleHistoryOffset"
    | "rollupsOffset";
  limit: number;
  offset: number;
  total: number;
  hasNext: boolean;
}

export async function TablePagination({
  query,
  offsetKey,
  limit,
  offset,
  total,
  hasNext,
}: TablePaginationProps) {
  const t = await getTranslations();
  const start = total === 0 ? 0 : offset + 1;
  const end = Math.min(offset + limit, total);
  const previousOffset = Math.max(0, offset - limit);
  const previousQuery = { [offsetKey]: previousOffset };
  const nextQuery = { [offsetKey]: offset + limit };

  return (
    <div className="mt-4 flex flex-col gap-3 text-sm font-bold text-neutral-700 md:flex-row md:items-center md:justify-between">
      <p>
        {t("energy.paginationSummary", {
          start,
          end,
          total,
        })}
      </p>
      <div className="flex gap-3">
        <Link
          href={buildEnergyHref(previousQuery, query)}
          scroll={false}
          aria-disabled={offset === 0}
          className="border-[3px] border-neutral-950 bg-white px-4 py-2 text-xs font-black uppercase tracking-[0.14em] text-neutral-950 aria-disabled:pointer-events-none aria-disabled:opacity-40"
        >
          {t("common.previous")}
        </Link>
        <Link
          href={buildEnergyHref(nextQuery, query)}
          scroll={false}
          aria-disabled={!hasNext}
          className="border-[3px] border-neutral-950 bg-neutral-950 px-4 py-2 text-xs font-black uppercase tracking-[0.14em] text-white aria-disabled:pointer-events-none aria-disabled:opacity-40"
        >
          {t("common.next")}
        </Link>
      </div>
    </div>
  );
}
