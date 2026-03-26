export type Trend = "up" | "down" | "stable";

export interface DomainSummary {
  label: string;
  value: string;
  change?: number;
  trend?: Trend;
  subtitle?: string;
}
