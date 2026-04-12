export interface DseStockRead {
  symbol: string;
  exchange_code: string;
  trade_date: string;

  // Raw numeric values
  close_price: number;
  open_price: number | null;
  high_price: number | null;
  low_price: number | null;
  change_pct: number | null;
  turnover_tzs: number | null;

  // Backend-formatted display strings — render these directly, no formatting needed
  close_price_display: string;
  open_price_display: string;
  high_price_display: string;
  low_price_display: string;
  change_pct_display: string;
  change_direction: "up" | "down" | "unchanged";
  turnover_display: string;
}

export interface DseDashboardSummaryRead {
  trade_date: string | null;
  total_symbols: number;
  total_turnover: number;
  total_turnover_display: string;
  top_gainer: DseStockRead | null;
  top_loser: DseStockRead | null;
  most_traded: DseStockRead | null;
  gainers_count: number;
  losers_count: number;
  unchanged_count: number;
}

export interface DseStockPage {
  items: DseStockRead[];
  meta: {
    limit: number;
    offset: number;
    total: number;
    has_next: boolean;
  };
}
