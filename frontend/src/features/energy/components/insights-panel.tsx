import { Badge } from "@/components/ui/badge";
import { SectionHeader } from "@/components/ui/section-header";
import type { EwuraFuelInsightRead } from "@/types/api";
import { getTranslations } from "next-intl/server";

interface InsightsPanelProps {
  insights: EwuraFuelInsightRead[];
}

export async function InsightsPanel({ insights }: InsightsPanelProps) {
  const t = await getTranslations();

  return (
    <div>
      <SectionHeader title={t("energy.insights")} description={t("energy.insightsDescription")} />
      <div className="grid gap-4 lg:grid-cols-2">
        {insights.length > 0 ? (
          insights.map((insight) => (
            <article
              key={`${insight.title}-${insight.fuel_type ?? "all"}`}
              className="border-[3px] border-neutral-950 bg-white p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
            >
              <div className="mb-3 flex items-center gap-3">
                {insight.fuel_type ? (
                  <Badge>{t(`energy.fuelLabels.${insight.fuel_type}`)}</Badge>
                ) : null}
                <span className="text-xs font-black uppercase tracking-[0.2em] text-neutral-400">
                  {t("energy.insight")}
                </span>
              </div>
              <h3 className="text-lg font-black text-neutral-950">{insight.title}</h3>
              <p className="mt-3 text-sm font-medium leading-6 text-neutral-600">{insight.body}</p>
            </article>
          ))
        ) : (
          <div className="border-[3px] border-dashed border-neutral-300 bg-white p-6 text-sm font-bold text-neutral-500">
            {t("common.noData")}
          </div>
        )}
      </div>
    </div>
  );
}
