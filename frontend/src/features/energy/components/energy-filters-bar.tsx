import { ROUTES } from "@/lib/constants";
import { SectionHeader } from "@/components/ui/section-header";
import type { EwuraFuelFiltersRead } from "@/types/api";
import { getTranslations } from "next-intl/server";
import type { EnergyQueryState } from "../types";

interface EnergyFiltersBarProps {
  filters: EwuraFuelFiltersRead;
  query: EnergyQueryState;
}

export async function EnergyFiltersBar({ filters, query }: EnergyFiltersBarProps) {
  const t = await getTranslations();

  return (
    <div className="space-y-4">
      <SectionHeader
        title={t("energy.filters")}
        description={
          filters.retail_latest_snapshot_month_label
            ? t("energy.filtersDescription", {
                retailMonth: filters.retail_latest_snapshot_month_label,
                wholesaleMonth:
                  filters.wholesale_latest_snapshot_month_label ?? t("energy.notAvailable"),
              })
            : t("energy.filtersDescriptionFallback")
        }
      />
      <form
        action={ROUTES.energy}
        method="get"
        className="grid gap-4 border-[3px] border-neutral-950 bg-[#f7f1df] p-5 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] md:grid-cols-5"
      >
        <label className="space-y-2 text-sm font-black uppercase tracking-[0.16em] text-neutral-900">
          <span>{t("energy.fuelType")}</span>
          <select
            name="fuelType"
            defaultValue={query.fuelType ?? ""}
            className="w-full border-[3px] border-neutral-950 bg-white px-3 py-3 text-sm font-bold uppercase tracking-[0.08em] outline-none"
          >
            <option value="">{t("energy.allFuelTypes")}</option>
            {filters.fuel_types.map((fuelType) => (
              <option key={fuelType} value={fuelType}>
                {t(`energy.fuelLabels.${fuelType}`)}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-2 text-sm font-black uppercase tracking-[0.16em] text-neutral-900">
          <span>{t("energy.location")}</span>
          <input
            type="search"
            name="locationQuery"
            defaultValue={query.locationQuery ?? ""}
            placeholder={t("energy.locationPlaceholder")}
            className="w-full border-[3px] border-neutral-950 bg-white px-3 py-3 text-sm font-bold outline-none"
          />
        </label>
        <label className="space-y-2 text-sm font-black uppercase tracking-[0.16em] text-neutral-900">
          <span>{t("energy.historyYear")}</span>
          <select
            name="retailHistoryYear"
            defaultValue={query.retailHistoryYear ? String(query.retailHistoryYear) : ""}
            className="w-full border-[3px] border-neutral-950 bg-white px-3 py-3 text-sm font-bold uppercase tracking-[0.08em] outline-none"
          >
            <option value="">{t("energy.retailHistoryOnDemand")}</option>
            {filters.retail_history_years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-2 text-sm font-black uppercase tracking-[0.16em] text-neutral-900">
          <span>{t("energy.wholesaleHistoryYear")}</span>
          <select
            name="wholesaleHistoryYear"
            defaultValue={query.wholesaleHistoryYear ? String(query.wholesaleHistoryYear) : ""}
            className="w-full border-[3px] border-neutral-950 bg-white px-3 py-3 text-sm font-bold uppercase tracking-[0.08em] outline-none"
          >
            <option value="">{t("energy.wholesaleHistoryOnDemand")}</option>
            {filters.wholesale_history_years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-end gap-3">
          <button
            type="submit"
            className="border-[3px] border-neutral-950 bg-neutral-950 px-4 py-3 text-sm font-black uppercase tracking-[0.14em] text-white"
          >
            {t("common.applyFilters")}
          </button>
          <a
            href={ROUTES.energy}
            className="border-[3px] border-neutral-950 bg-white px-4 py-3 text-sm font-black uppercase tracking-[0.14em] text-neutral-950"
          >
            {t("common.clear")}
          </a>
        </div>
      </form>
    </div>
  );
}
