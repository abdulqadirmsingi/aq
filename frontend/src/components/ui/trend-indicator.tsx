import { cn } from "@/lib/utils";
import type { Trend } from "@/types";

interface TrendIndicatorProps {
  trend: Trend;
  value: number;
}

const trendConfig: Record<Trend, { symbol: string; className: string }> = {
  up: { symbol: "\u2191", className: "text-emerald-600" },
  down: { symbol: "\u2193", className: "text-red-600" },
  stable: { symbol: "\u2192", className: "text-neutral-500" },
};

export function TrendIndicator({ trend, value }: TrendIndicatorProps) {
  const config = trendConfig[trend];

  return (
    <span className={cn("inline-flex items-center text-xs font-medium", config.className)}>
      {config.symbol} {Math.abs(value)}%
    </span>
  );
}
