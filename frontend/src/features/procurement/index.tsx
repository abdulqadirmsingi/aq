import type { TenderFiltersRead, TenderPage } from "@/types/api";
import { ProcurementSummaryCards } from "./components/procurement-summary-cards";
import { TenderTable } from "./components/tender-table";

interface ProcurementFeatureProps {
  tenders: TenderPage;
  filters: TenderFiltersRead;
  offset: number;
}

export function ProcurementFeature({ tenders, filters, offset }: ProcurementFeatureProps) {
  return (
    <div className="space-y-8">
      <ProcurementSummaryCards filters={filters} total={tenders.meta.total} />
      <TenderTable page={tenders} currentOffset={offset} />
    </div>
  );
}
