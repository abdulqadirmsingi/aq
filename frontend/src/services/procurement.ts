import { API_ENDPOINTS } from "@/lib/constants";
import type { TenderFiltersRead, TenderPage } from "@/types/api";
import { apiFetch } from "./api-client";

export interface TenderListOptions {
  limit?: number;
  offset?: number;
  tender_status?: string;
  has_award?: boolean;
  procurement_method?: string;
  search?: string;
}

export async function getTenders(options: TenderListOptions = {}): Promise<TenderPage> {
  return apiFetch<TenderPage>(API_ENDPOINTS.procurement.tenders, {
    query: {
      limit: options.limit ?? 50,
      offset: options.offset ?? 0,
      tender_status: options.tender_status,
      has_award: options.has_award,
      procurement_method: options.procurement_method,
      search: options.search,
    },
    revalidate: 3600,
  });
}

export async function getTenderFilters(): Promise<TenderFiltersRead> {
  return apiFetch<TenderFiltersRead>(API_ENDPOINTS.procurement.filters, {
    revalidate: 3600,
  });
}

export async function getProcurementPageData(options: TenderListOptions = {}): Promise<{
  tenders: TenderPage;
  filters: TenderFiltersRead;
}> {
  const [tenders, filters] = await Promise.all([
    getTenders(options).catch(() => emptyPage()),
    getTenderFilters().catch(() => emptyFilters()),
  ]);
  return { tenders, filters };
}

function emptyPage(): TenderPage {
  return { items: [], meta: { limit: 50, offset: 0, total: 0, has_next: false } };
}

function emptyFilters(): TenderFiltersRead {
  return {
    tender_statuses: [],
    procurement_methods: [],
    financial_years: [],
    procuring_entities: [],
    total_published: 0,
    total_awarded: 0,
  };
}
