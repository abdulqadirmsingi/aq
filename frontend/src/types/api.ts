export type { ApiPage, ApiPageMeta } from "./api/common";
export type {
  EwuraFuelAvailableMonthRead,
  EwuraFuelDashboardSummaryRead,
  EwuraFuelExtremeItemRead,
  EwuraFuelInsightRead,
  EwuraFuelLatestExtremesRead,
  EwuraFuelLatestPriceRead,
  EwuraFuelLatestSummaryItemRead,
  EwuraFuelLatestSummaryRead,
  EwuraFuelMonthlyTrendRead,
  EwuraFuelObservationPage,
  EwuraFuelObservationRead,
  EwuraFuelRollupRead,
  EwuraFuelRunLogPage,
  EwuraFuelRunLogRead,
  EwuraFuelRunPage,
  EwuraFuelRunRead,
} from "./api/energy";

export interface ExchangeRate {
  id: string;
  currencyPair: string;
  buyRate: number;
  sellRate: number;
  previousBuyRate: number;
  date: string;
}

export interface InflationRecord {
  id: string;
  month: string;
  rate: number;
  previousRate: number;
  yearOverYear: number;
}

export interface RentPrice {
  id: string;
  area: string;
  propertyType: string;
  bedrooms: number;
  monthlyRent: number;
  previousRent: number;
}

export interface LandPrice {
  id: string;
  location: string;
  pricePerSqm: number;
  previousPrice: number;
  category: string;
}

export interface DrugPrice {
  id: string;
  drugName: string;
  genericName: string;
  dosage: string;
  minPrice: number;
  maxPrice: number;
  availability: "available" | "limited" | "scarce";
}

export interface Salary {
  id: string;
  role: string;
  sector: string;
  avgSalary: number;
  minSalary: number;
  maxSalary: number;
  experience: string;
}

export interface JobTrend {
  id: string;
  role: string;
  sector: string;
  demand: "growing" | "declining" | "stable";
  openings: number;
  changePercent: number;
}
