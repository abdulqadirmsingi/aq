export type { ApiPage, ApiPageMeta } from "./api/common";
export type { DseDashboardSummaryRead, DseStockPage, DseStockRead } from "./api/dse";
export type {
  EwuraFuelAvailableMonthRead,
  EwuraFuelDashboardSummaryRead,
  EwuraFuelExtremeItemRead,
  EwuraFuelFiltersRead,
  EwuraFuelInsightRead,
  EwuraFuelLatestExtremesRead,
  EwuraFuelLatestPricePage,
  EwuraFuelLatestPriceRead,
  EwuraFuelLatestSummaryItemRead,
  EwuraFuelLatestSummaryRead,
  EwuraFuelMonthlyTrendRead,
  EwuraFuelObservationPage,
  EwuraFuelObservationRead,
  EwuraFuelRollupPage,
  EwuraFuelRollupRead,
  EwuraFuelRunLogPage,
  EwuraFuelRunLogRead,
  EwuraFuelRunPage,
  EwuraFuelRunRead,
} from "./api/energy";
export type {
  BotExchangeRateAvailableMonthRead,
  BotExchangeRateFiltersRead,
  BotExchangeRatePage,
  BotExchangeRateRead,
  ExchangeRateBenchmarkGapRead,
  ExchangeRateBenchmarkGapSummaryRead,
  ExchangeRateBestRateRead,
  ExchangeRateBestRateSummaryRead,
  ExchangeRateComparisonRead,
  ExchangeRateLatestComparisonRead,
  ExchangeRateOpportunityRead,
  ExchangeRateOpportunitySummaryRead,
  ExchangeRateRecommendationCandidateRead,
  ExchangeRateRecommendationRead,
  ExchangeRateSpreadRead,
  ExchangeRateSpreadSummaryRead,
  ExchangeRateStalenessRead,
  ExchangeRateStalenessSummaryRead,
  MoneyDashboardSummaryRead,
} from "./api/money";

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
