import { cn } from "@/lib/utils";
import type { Trend } from "@/types";
import { TrendIndicator } from "./trend-indicator";

interface DataCardProps {
  title: string;
  value: string;
  change?: number;
  trend?: Trend;
  subtitle?: string;
  variant?: "default" | "featured" | "compact";
  className?: string;
}

export function DataCard({ title, value, change, trend, subtitle, variant = "default", className }: DataCardProps) {
  const isFeatured = variant === "featured";
  
  return (
    <div className={cn(
      "group relative flex flex-col justify-between overflow-hidden border-[3px] border-neutral-950 bg-white p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]",
      className
    )}>
      <div className="relative z-10">
        <div className="flex items-center justify-between">
          <p className="text-xs font-black uppercase tracking-[0.2em] text-neutral-400 group-hover:text-neutral-900 transition-colors">
            {title}
          </p>
          {trend && change !== undefined && (
            <div className="scale-110">
              <TrendIndicator trend={trend} value={change} />
            </div>
          )}
        </div>
        
        <div className="mt-6">
          <span className={cn(
            "block font-black tracking-tighter text-neutral-950 transition-all duration-300 group-hover:tracking-normal",
            isFeatured ? "text-6xl md:text-8xl" : "text-4xl md:text-5xl"
          )}>
            {value}
          </span>
        </div>
      </div>
      
      {subtitle && (
        <div className="mt-8 pt-6 border-t-[1px] border-neutral-100 group-hover:border-neutral-950 transition-colors">
          <p className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 group-hover:text-neutral-950">
            {subtitle}
          </p>
        </div>
      )}

      {/* Experimental brutalist corner */}
      <div className="absolute top-0 right-0 w-12 h-12 bg-neutral-950 translate-x-6 -translate-y-6 rotate-45 group-hover:translate-x-4 group-hover:-translate-y-4 transition-transform" />
    </div>
  );
}
