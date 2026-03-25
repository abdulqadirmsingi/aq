import { cn } from "@/lib/utils";
import type { Trend } from "@/types";
import { TrendIndicator } from "./trend-indicator";

interface DataCardProps {
  title: string;
  value: string;
  change?: number;
  trend?: Trend;
  subtitle?: string;
}

export function DataCard({ title, value, change, trend, subtitle }: DataCardProps) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5">
      <p className="text-sm font-medium text-neutral-500">{title}</p>
      <div className="mt-2 flex items-end gap-2">
        <span className="text-2xl font-semibold tracking-tight text-neutral-900">{value}</span>
        {trend && change !== undefined && <TrendIndicator trend={trend} value={change} />}
      </div>
      {subtitle && <p className={cn("mt-1 text-xs text-neutral-400")}>{subtitle}</p>}
    </div>
  );
}
