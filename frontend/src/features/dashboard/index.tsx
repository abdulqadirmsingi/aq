"use client";

import type { DomainSummary } from "@/types";
import { SummaryCards } from "./components/summary-cards";

interface DashboardFeatureProps {
  summaries: DomainSummary[];
}

export function DashboardFeature({ summaries }: DashboardFeatureProps) {
  return <SummaryCards summaries={summaries} />;
}
