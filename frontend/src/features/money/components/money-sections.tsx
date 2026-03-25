import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { formatNumber } from "@/lib/utils";
import type {
  BotExchangeRateRead,
  ExchangeRateBenchmarkGapRead,
  ExchangeRateComparisonRead,
  ExchangeRateOpportunityRead,
  ExchangeRateRecommendationRead,
  ExchangeRateSpreadRead,
  ExchangeRateStalenessRead,
} from "@/types/api";
import { getTranslations } from "next-intl/server";
import { buildMoneyHref } from "../query";
import type { MoneyQueryState } from "../types";

function formatRate(value: number | null | undefined): string {
  return value === null || value === undefined ? "N/A" : formatNumber(value);
}

function formatSigned(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "N/A";
  }
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${formatNumber(value)}`;
}

function sourceBadgeVariant(sourceSlug: string): "default" | "success" | "warning" {
  if (sourceSlug === "bot_exchange_rates") {
    return "success";
  }
  if (sourceSlug === "nmb_daily_exchange_rates") {
    return "warning";
  }
  return "default";
}

export async function RecommendationPanel({
  recommendation,
}: {
  recommendation: ExchangeRateRecommendationRead;
}) {
  const t = await getTranslations();
  const best = recommendation.best_option;

  return (
    <div className="grid gap-6 lg:grid-cols-[1.25fr_1fr]">
      <div className="border-[3px] border-neutral-950 bg-white p-6 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        <SectionHeader
          title={t("money.recommendation")}
          description={t("money.recommendationDescription", {
            action: recommendation.customer_action === "buy" ? t("money.actionBuy") : t("money.actionSell"),
            instrument: recommendation.instrument_code,
          })}
        />
        {best ? (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <Badge variant={sourceBadgeVariant(best.source_slug)}>{best.source_name}</Badge>
              <Badge>{best.rate_label}</Badge>
              {best.channel ? <Badge>{best.channel}</Badge> : null}
              {best.cash_note_band ? <Badge>{best.cash_note_band}</Badge> : null}
            </div>
            <div>
              <p className="text-sm font-bold uppercase tracking-[0.18em] text-neutral-500">
                {t("money.bestRate")}
              </p>
              <p className="mt-2 text-4xl font-black tracking-tight text-neutral-950">
                {formatRate(best.relevant_rate)} TZS
              </p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-neutral-500">
                  {t("money.buyRate")}
                </p>
                <p className="mt-2 text-lg font-bold text-neutral-950">
                  {formatRate(best.buy_rate)}
                </p>
              </div>
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-neutral-500">
                  {t("money.sellRate")}
                </p>
                <p className="mt-2 text-lg font-bold text-neutral-950">
                  {formatRate(best.sell_rate)}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm font-bold text-neutral-500">{t("common.noData")}</p>
        )}
      </div>

      <div className="border-[3px] border-neutral-950 bg-neutral-950 p-6 text-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        <SectionHeader
          title={t("money.botBenchmark")}
          description={t("money.botBenchmarkDescription")}
        />
        {recommendation.benchmark ? (
          <div className="space-y-3">
            <p className="text-3xl font-black tracking-tight">
              {formatRate(recommendation.benchmark.mean_rate)} TZS
            </p>
            <p className="text-sm font-bold text-neutral-300">
              {recommendation.benchmark.source_name}
            </p>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-neutral-400">
              {recommendation.benchmark.snapshot_month_label}
            </p>
          </div>
        ) : (
          <p className="text-sm font-bold text-neutral-400">{t("common.noData")}</p>
        )}
      </div>
    </div>
  );
}

export async function ComparisonTable({
  items,
}: {
  items: ExchangeRateComparisonRead[];
}) {
  const t = await getTranslations();

  const columns = [
    {
      key: "source",
      header: t("common.source"),
      render: (item: ExchangeRateComparisonRead) => (
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={sourceBadgeVariant(item.source_slug)}>{item.source_name}</Badge>
          {item.channel ? <Badge>{item.channel}</Badge> : null}
          {item.cash_note_band ? <Badge>{item.cash_note_band}</Badge> : null}
        </div>
      ),
    },
    {
      key: "buy",
      header: t("money.buyRate"),
      render: (item: ExchangeRateComparisonRead) => formatRate(item.buy_rate),
    },
    {
      key: "sell",
      header: t("money.sellRate"),
      render: (item: ExchangeRateComparisonRead) => formatRate(item.sell_rate),
    },
    {
      key: "mean",
      header: t("money.meanRate"),
      render: (item: ExchangeRateComparisonRead) => formatRate(item.mean_rate),
    },
    {
      key: "updated",
      header: t("common.lastUpdated"),
      render: (item: ExchangeRateComparisonRead) =>
        item.source_last_updated_at ?? item.source_effective_date ?? item.snapshot_date,
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("money.latestComparison")}
        description={t("money.latestComparisonDescription")}
      />
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(item) => `${item.source_slug}:${item.instrument_code}:${item.channel ?? "na"}:${item.cash_note_band ?? "na"}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}

export async function SpreadTable({ items }: { items: ExchangeRateSpreadRead[] }) {
  const t = await getTranslations();

  const columns = [
    {
      key: "source",
      header: t("common.source"),
      render: (item: ExchangeRateSpreadRead) => (
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={sourceBadgeVariant(item.source_slug)}>{item.source_name}</Badge>
          {item.channel ? <Badge>{item.channel}</Badge> : null}
        </div>
      ),
    },
    {
      key: "buy",
      header: t("money.buyRate"),
      render: (item: ExchangeRateSpreadRead) => formatRate(item.buy_rate),
    },
    {
      key: "sell",
      header: t("money.sellRate"),
      render: (item: ExchangeRateSpreadRead) => formatRate(item.sell_rate),
    },
    {
      key: "spread",
      header: t("money.spread"),
      render: (item: ExchangeRateSpreadRead) => formatRate(item.spread),
    },
    {
      key: "spreadPercent",
      header: t("money.spreadPercent"),
      render: (item: ExchangeRateSpreadRead) =>
        item.spread_percent_of_buy === null ? "N/A" : `${formatNumber(item.spread_percent_of_buy)}%`,
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("money.spreadSummary")}
        description={t("money.spreadSummaryDescription")}
      />
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(item) => `${item.source_slug}:${item.instrument_code}:${item.channel ?? "na"}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}

export async function GapTable({ items }: { items: ExchangeRateBenchmarkGapRead[] }) {
  const t = await getTranslations();

  const columns = [
    {
      key: "source",
      header: t("common.source"),
      render: (item: ExchangeRateBenchmarkGapRead) => (
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={sourceBadgeVariant(item.source_slug)}>{item.source_name}</Badge>
          {item.channel ? <Badge>{item.channel}</Badge> : null}
        </div>
      ),
    },
    {
      key: "relevant",
      header: t("money.rateLabel"),
      render: (item: ExchangeRateBenchmarkGapRead) => formatRate(item.relevant_rate),
    },
    {
      key: "bot",
      header: t("money.botMean"),
      render: (item: ExchangeRateBenchmarkGapRead) => formatRate(item.bot_mean_rate),
    },
    {
      key: "gap",
      header: t("money.gapVsBot"),
      render: (item: ExchangeRateBenchmarkGapRead) => formatSigned(item.absolute_gap),
    },
    {
      key: "gapPercent",
      header: t("money.percentGap"),
      render: (item: ExchangeRateBenchmarkGapRead) =>
        item.percent_gap === null ? "N/A" : `${formatNumber(item.percent_gap)}%`,
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("money.benchmarkGaps")}
        description={t("money.benchmarkGapsDescription")}
      />
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(item) => `${item.source_slug}:${item.instrument_code}:${item.channel ?? "na"}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}

export async function OpportunityTable({
  items,
}: {
  items: ExchangeRateOpportunityRead[];
}) {
  const t = await getTranslations();

  const columns = [
    {
      key: "best",
      header: t("money.bestOption"),
      render: (item: ExchangeRateOpportunityRead) => (
        <Badge variant={sourceBadgeVariant(item.best_source_slug)}>{item.best_source_name}</Badge>
      ),
    },
    {
      key: "compared",
      header: t("money.comparedSource"),
      render: (item: ExchangeRateOpportunityRead) => (
        <Badge variant={sourceBadgeVariant(item.compared_source_slug)}>{item.compared_source_name}</Badge>
      ),
    },
    {
      key: "bestRate",
      header: t("money.bestRate"),
      render: (item: ExchangeRateOpportunityRead) => formatRate(item.best_rate),
    },
    {
      key: "currentRate",
      header: t("money.currentRate"),
      render: (item: ExchangeRateOpportunityRead) => formatRate(item.relevant_rate),
    },
    {
      key: "difference",
      header: t("money.opportunity"),
      render: (item: ExchangeRateOpportunityRead) => formatSigned(item.absolute_difference),
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("money.opportunities")}
        description={t("money.opportunitiesDescription")}
      />
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(item) => `${item.best_source_slug}:${item.compared_source_slug}:${item.instrument_code}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}

export async function StalenessTable({ items }: { items: ExchangeRateStalenessRead[] }) {
  const t = await getTranslations();

  const columns = [
    {
      key: "source",
      header: t("common.source"),
      render: (item: ExchangeRateStalenessRead) => (
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={item.is_freshest ? "success" : sourceBadgeVariant(item.source_slug)}>
            {item.source_name}
          </Badge>
          {item.channel ? <Badge>{item.channel}</Badge> : null}
        </div>
      ),
    },
    {
      key: "timestamp",
      header: t("money.dataTimestamp"),
      render: (item: ExchangeRateStalenessRead) => item.data_timestamp,
    },
    {
      key: "lag",
      header: t("money.stalenessLag"),
      render: (item: ExchangeRateStalenessRead) => `${formatNumber(item.lag_hours_vs_freshest)}h`,
    },
    {
      key: "freshest",
      header: t("money.freshness"),
      render: (item: ExchangeRateStalenessRead) =>
        item.is_freshest ? (
          <Badge variant="success">{t("money.freshest")}</Badge>
        ) : (
          <Badge>{t("money.staleRelative")}</Badge>
        ),
    },
  ];

  return (
    <div>
      <SectionHeader
        title={t("money.staleness")}
        description={t("money.stalenessDescription")}
      />
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(item) => `${item.source_slug}:${item.instrument_code}:${item.data_timestamp}`}
        emptyMessage={t("common.noData")}
      />
    </div>
  );
}

export async function BotHistoryTable({
  history,
  query,
}: {
  history: { items: BotExchangeRateRead[]; meta: { limit: number; offset: number; total: number; has_next: boolean } };
  query: MoneyQueryState;
}) {
  const t = await getTranslations();
  const columns = [
    {
      key: "month",
      header: t("money.month"),
      render: (item: BotExchangeRateRead) => item.snapshot_month_label,
    },
    {
      key: "buy",
      header: t("money.buyRate"),
      render: (item: BotExchangeRateRead) => formatRate(item.buy_rate),
    },
    {
      key: "sell",
      header: t("money.sellRate"),
      render: (item: BotExchangeRateRead) => formatRate(item.sell_rate),
    },
    {
      key: "mean",
      header: t("money.meanRate"),
      render: (item: BotExchangeRateRead) => formatRate(item.mean_rate),
    },
    {
      key: "date",
      header: t("common.date"),
      render: (item: BotExchangeRateRead) => item.snapshot_date,
    },
  ];

  const previousOffset = Math.max(0, history.meta.offset - history.meta.limit);

  return (
    <div>
      <SectionHeader
        title={t("money.botHistory")}
        description={t("money.botHistoryDescription")}
      />
      <DataTable
        columns={columns}
        data={history.items}
        keyExtractor={(item) => `${item.instrument_code}:${item.snapshot_date}`}
        emptyMessage={t("common.noData")}
      />
      <div className="mt-4 flex flex-col gap-3 text-sm font-bold text-neutral-700 md:flex-row md:items-center md:justify-between">
        <p>
          {t("money.historyPaginationSummary", {
            start: history.meta.total === 0 ? 0 : history.meta.offset + 1,
            end: Math.min(history.meta.offset + history.meta.limit, history.meta.total),
            total: history.meta.total,
          })}
        </p>
        <div className="flex gap-3">
          <Link
            href={buildMoneyHref({ historyOffset: previousOffset }, query)}
            scroll={false}
            aria-disabled={history.meta.offset === 0}
            className="border-[3px] border-neutral-950 bg-white px-4 py-2 text-xs font-black uppercase tracking-[0.14em] text-neutral-950 aria-disabled:pointer-events-none aria-disabled:opacity-40"
          >
            {t("common.previous")}
          </Link>
          <Link
            href={buildMoneyHref({ historyOffset: history.meta.offset + history.meta.limit }, query)}
            scroll={false}
            aria-disabled={!history.meta.has_next}
            className="border-[3px] border-neutral-950 bg-neutral-950 px-4 py-2 text-xs font-black uppercase tracking-[0.14em] text-white aria-disabled:pointer-events-none aria-disabled:opacity-40"
          >
            {t("common.next")}
          </Link>
        </div>
      </div>
    </div>
  );
}
