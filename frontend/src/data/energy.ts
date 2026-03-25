import type { ElectricityTariff, FuelPrice, GasPrice } from "@/types/api";

export const fuelPrices: FuelPrice[] = [
  {
    id: "f1",
    fuelType: "petrol",
    region: "Dar es Salaam",
    pricePerLitre: 3389,
    previousPrice: 3307,
    date: "2026-03-01",
  },
  {
    id: "f2",
    fuelType: "diesel",
    region: "Dar es Salaam",
    pricePerLitre: 3247,
    previousPrice: 3180,
    date: "2026-03-01",
  },
  {
    id: "f3",
    fuelType: "kerosene",
    region: "Dar es Salaam",
    pricePerLitre: 3120,
    previousPrice: 3095,
    date: "2026-03-01",
  },
  {
    id: "f4",
    fuelType: "petrol",
    region: "Arusha",
    pricePerLitre: 3452,
    previousPrice: 3370,
    date: "2026-03-01",
  },
  {
    id: "f5",
    fuelType: "diesel",
    region: "Arusha",
    pricePerLitre: 3310,
    previousPrice: 3245,
    date: "2026-03-01",
  },
  {
    id: "f6",
    fuelType: "kerosene",
    region: "Arusha",
    pricePerLitre: 3185,
    previousPrice: 3150,
    date: "2026-03-01",
  },
  {
    id: "f7",
    fuelType: "petrol",
    region: "Dodoma",
    pricePerLitre: 3478,
    previousPrice: 3395,
    date: "2026-03-01",
  },
  {
    id: "f8",
    fuelType: "diesel",
    region: "Dodoma",
    pricePerLitre: 3335,
    previousPrice: 3270,
    date: "2026-03-01",
  },
];

export const gasPrices: GasPrice[] = [
  { id: "g1", gasType: "LPG", weight: "6 kg", price: 28000, previousPrice: 27000, date: "2026-03-01" },
  { id: "g2", gasType: "LPG", weight: "15 kg", price: 65000, previousPrice: 63000, date: "2026-03-01" },
  { id: "g3", gasType: "LPG", weight: "38 kg", price: 155000, previousPrice: 150000, date: "2026-03-01" },
  { id: "g4", gasType: "Natural Gas", weight: "per m³", price: 850, previousPrice: 820, date: "2026-03-01" },
];

export const electricityTariffs: ElectricityTariff[] = [
  { id: "e1", category: "Domestic (D1)", ratePerKwh: 100, previousRate: 100, description: "0-75 kWh" },
  { id: "e2", category: "Domestic (D1)", ratePerKwh: 350, previousRate: 340, description: "Above 75 kWh" },
  { id: "e3", category: "General (T1)", ratePerKwh: 275, previousRate: 265, description: "Commercial low voltage" },
  { id: "e4", category: "Industrial (T2)", ratePerKwh: 205, previousRate: 200, description: "Industrial medium voltage" },
  { id: "e5", category: "Industrial (T3)", ratePerKwh: 155, previousRate: 150, description: "Industrial high voltage" },
];
