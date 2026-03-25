import type { LandPrice, RentPrice } from "@/types/api";

export const rentPrices: RentPrice[] = [
  { id: "r1", area: "Masaki", propertyType: "Apartment", bedrooms: 2, monthlyRent: 1800000, previousRent: 1750000 },
  { id: "r2", area: "Masaki", propertyType: "Apartment", bedrooms: 3, monthlyRent: 2500000, previousRent: 2400000 },
  { id: "r3", area: "Mikocheni", propertyType: "Apartment", bedrooms: 2, monthlyRent: 800000, previousRent: 780000 },
  { id: "r4", area: "Mikocheni", propertyType: "House", bedrooms: 3, monthlyRent: 1200000, previousRent: 1150000 },
  { id: "r5", area: "Kinondoni", propertyType: "Apartment", bedrooms: 1, monthlyRent: 450000, previousRent: 430000 },
  { id: "r6", area: "Kinondoni", propertyType: "House", bedrooms: 2, monthlyRent: 700000, previousRent: 680000 },
  { id: "r7", area: "Mbezi Beach", propertyType: "House", bedrooms: 3, monthlyRent: 900000, previousRent: 870000 },
  { id: "r8", area: "Kigamboni", propertyType: "House", bedrooms: 2, monthlyRent: 350000, previousRent: 340000 },
];

export const landPrices: LandPrice[] = [
  { id: "l1", location: "Masaki", pricePerSqm: 850000, previousPrice: 820000, category: "Commercial" },
  { id: "l2", location: "Mikocheni", pricePerSqm: 450000, previousPrice: 430000, category: "Residential" },
  { id: "l3", location: "Mbezi Beach", pricePerSqm: 180000, previousPrice: 170000, category: "Residential" },
  { id: "l4", location: "Kigamboni", pricePerSqm: 85000, previousPrice: 80000, category: "Residential" },
  { id: "l5", location: "Dodoma CBD", pricePerSqm: 250000, previousPrice: 240000, category: "Commercial" },
  { id: "l6", location: "Arusha Centre", pricePerSqm: 350000, previousPrice: 340000, category: "Commercial" },
];
