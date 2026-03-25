import { jobTrends, salaries } from "@/data/hr";
import type { JobTrend, Salary } from "@/types/api";
import { simulateFetch } from "./api-client";

export async function getSalaries(): Promise<Salary[]> {
  return simulateFetch(salaries);
}

export async function getJobTrends(): Promise<JobTrend[]> {
  return simulateFetch(jobTrends);
}
