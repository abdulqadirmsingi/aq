export interface TenderRead {
  id: string;
  ocid: string;
  tender_reference: string;
  title: string;
  description: string | null;
  procuring_entity_name: string | null;
  procuring_entity_id: string | null;
  procurement_method: string | null;
  procurement_method_details: string | null;
  tender_status: string | null;
  tender_value_amount: string | null;
  tender_value_currency: string | null;
  tender_period_start: string | null;
  tender_period_end: string | null;
  has_award: boolean;
  award_date: string | null;
  award_value_amount: string | null;
  award_value_currency: string | null;
  contractor_name: string | null;
  contractor_id: string | null;
  financial_year: string | null;
  location: string | null;
  source_url: string | null;
  fetched_at: string;
  created_at: string;
  updated_at: string;
}

export interface TenderFiltersRead {
  tender_statuses: string[];
  procurement_methods: string[];
  financial_years: string[];
  procuring_entities: string[];
  total_published: number;
  total_awarded: number;
}

export interface TenderPage {
  items: TenderRead[];
  meta: {
    limit: number;
    offset: number;
    total: number;
    has_next: boolean;
  };
}
