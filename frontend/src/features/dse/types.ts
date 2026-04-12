import type { DseDashboardSummaryRead, DseStockPage } from "@/types/api";

export interface DsePageData {
  summary: DseDashboardSummaryRead;
  latest: DseStockPage;
}
