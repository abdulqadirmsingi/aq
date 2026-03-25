"use client";

import type { JobTrend, Salary } from "@/types/api";
import { JobTrendTable } from "./components/job-trend-table";
import { SalaryTable } from "./components/salary-table";

interface HrFeatureProps {
  salaries: Salary[];
  jobTrends: JobTrend[];
}

export function HrFeature({ salaries, jobTrends }: HrFeatureProps) {
  return (
    <div className="space-y-8">
      <SalaryTable data={salaries} />
      <JobTrendTable data={jobTrends} />
    </div>
  );
}
