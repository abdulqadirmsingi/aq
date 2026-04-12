import { API_ENDPOINTS } from "@/lib/constants";
import type { DseDashboardSummaryRead, DseStockPage } from "@/types/api";
import { apiFetch } from "./api-client";

export async function getDseDashboardSummary(): Promise<DseDashboardSummaryRead> {
  return apiFetch<DseDashboardSummaryRead>(API_ENDPOINTS.dse.dashboardSummary);
}

export async function getDseLatestStocks(options?: {
  limit?: number;
  offset?: number;
  symbol?: string;
}): Promise<DseStockPage> {
  return apiFetch<DseStockPage>(API_ENDPOINTS.dse.latest, {
    query: {
      limit: options?.limit ?? 100,
      offset: options?.offset ?? 0,
      symbol: options?.symbol,
    },
  });
}

export async function getDseStockHistory(
  symbol: string,
  options?: { limit?: number; offset?: number },
): Promise<DseStockPage> {
  return apiFetch<DseStockPage>(API_ENDPOINTS.dse.history, {
    query: {
      symbol,
      limit: options?.limit ?? 30,
      offset: options?.offset ?? 0,
    },
  });
}

export async function getDsePageData(): Promise<{
  summary: DseDashboardSummaryRead;
  latest: DseStockPage;
}> {
  const [summary, latest] = await Promise.all([
    getDseDashboardSummary().catch(() => emptySummary()),
    getDseLatestStocks().catch(() => emptyPage()),
  ]);
  return { summary, latest };
}

function emptySummary(): DseDashboardSummaryRead {
  return {
    trade_date: null,
    total_symbols: 0,
    total_turnover: 0,
    top_gainer: null,
    top_loser: null,
    most_traded: null,
    gainers_count: 0,
    losers_count: 0,
    unchanged_count: 0,
  };
}

function emptyPage(): DseStockPage {
  return { items: [], meta: { limit: 100, offset: 0, total: 0, has_next: false } };
}
