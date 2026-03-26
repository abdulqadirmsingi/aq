import { ENERGY_DEFAULTS, API_ENDPOINTS } from "@/lib/constants";
import type { EnergyMonitoringPageData } from "@/features/energy-monitoring/types";
import type { EwuraFuelRunLogPage, EwuraFuelRunPage } from "@/types/api";
import { apiFetch } from "./api-client";

interface RunsOptions {
  status?: string;
  limit?: number;
  offset?: number;
}

interface RunLogsOptions {
  level?: string;
  eventType?: string;
  limit?: number;
  offset?: number;
}

function getRunLogsPath(runId: string): string {
  return `${API_ENDPOINTS.energy.ewura.runs}/${runId}/logs`;
}

function emptyRunPage(limit = ENERGY_DEFAULTS.runsLimit): EwuraFuelRunPage {
  return {
    items: [],
    meta: {
      limit,
      offset: 0,
      total: 0,
      has_next: false,
    },
  };
}

function emptyRunLogPage(limit = ENERGY_DEFAULTS.runLogsLimit): EwuraFuelRunLogPage {
  return {
    items: [],
    meta: {
      limit,
      offset: 0,
      total: 0,
      has_next: false,
    },
  };
}

async function safeRequest<T>(loader: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await loader();
  } catch {
    return fallback;
  }
}

export async function getEnergyRuns(options: RunsOptions = {}): Promise<EwuraFuelRunPage> {
  return apiFetch<EwuraFuelRunPage>(API_ENDPOINTS.energy.ewura.runs, {
    query: {
      status: options.status,
      limit: options.limit ?? ENERGY_DEFAULTS.runsLimit,
      offset: options.offset ?? 0,
    },
  });
}

export async function getEnergyRunLogs(
  runId: string,
  options: RunLogsOptions = {},
): Promise<EwuraFuelRunLogPage> {
  return apiFetch<EwuraFuelRunLogPage>(getRunLogsPath(runId), {
    query: {
      level: options.level,
      event_type: options.eventType,
      limit: options.limit ?? ENERGY_DEFAULTS.runLogsLimit,
      offset: options.offset ?? 0,
    },
  });
}

export async function getEnergyMonitoringPageData(): Promise<EnergyMonitoringPageData> {
  const runs = await safeRequest(() => getEnergyRuns(), emptyRunPage());
  const latestRun = runs.items[0];
  const runLogs = latestRun
    ? await safeRequest(() => getEnergyRunLogs(latestRun.id), emptyRunLogPage())
    : null;

  return { runs, runLogs };
}
