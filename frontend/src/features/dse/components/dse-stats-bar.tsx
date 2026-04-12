import { getTranslations } from "next-intl/server";
import type { DseDashboardSummaryRead } from "@/types/api";

interface DseStatsBarProps {
  summary: DseDashboardSummaryRead;
}

export async function DseStatsBar({ summary }: DseStatsBarProps) {
  const t = await getTranslations();

  const stats = [
    { label: t("dse.gainers"), value: summary.gainers_count, color: "text-emerald-600" },
    { label: t("dse.losers"), value: summary.losers_count, color: "text-red-600" },
    { label: t("dse.unchanged"), value: summary.unchanged_count, color: "text-neutral-600" },
    { label: t("dse.totalSymbols"), value: summary.total_symbols, color: "text-neutral-900" },
  ];

  return (
    <div className="border-[3px] border-neutral-950 bg-neutral-950 p-5 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
      <div className="flex flex-wrap items-center gap-8">
        <div>
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400">
            {t("dse.exchange")}
          </p>
          <p className="mt-1 text-sm font-black text-white">Dar es Salaam Stock Exchange</p>
        </div>

        <div className="h-8 w-px bg-neutral-700 hidden sm:block" />

        {stats.map((stat) => (
          <div key={stat.label}>
            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400">
              {stat.label}
            </p>
            <p className={`mt-1 text-xl font-black ${stat.color}`}>{stat.value}</p>
          </div>
        ))}

        <div className="ml-auto hidden sm:block">
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-neutral-400">
            {t("dse.source")}
          </p>
          <p className="mt-1 text-xs font-bold text-neutral-300">iTrust Finance</p>
        </div>
      </div>
    </div>
  );
}
