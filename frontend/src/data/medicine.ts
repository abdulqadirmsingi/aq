import type { DrugPrice } from "@/types/api";

export const drugPrices: DrugPrice[] = [
  { id: "d1", drugName: "Panadol", genericName: "Paracetamol", dosage: "500mg", minPrice: 500, maxPrice: 1500, availability: "available" },
  { id: "d2", drugName: "Amoxil", genericName: "Amoxicillin", dosage: "500mg", minPrice: 800, maxPrice: 2500, availability: "available" },
  { id: "d3", drugName: "Flagyl", genericName: "Metronidazole", dosage: "400mg", minPrice: 600, maxPrice: 1800, availability: "available" },
  { id: "d4", drugName: "Augmentin", genericName: "Amoxicillin/Clavulanate", dosage: "625mg", minPrice: 3000, maxPrice: 8000, availability: "limited" },
  { id: "d5", drugName: "Coartem", genericName: "Artemether/Lumefantrine", dosage: "20/120mg", minPrice: 2500, maxPrice: 5000, availability: "available" },
  { id: "d6", drugName: "Metformin", genericName: "Metformin HCl", dosage: "500mg", minPrice: 400, maxPrice: 1200, availability: "available" },
  { id: "d7", drugName: "Losartan", genericName: "Losartan Potassium", dosage: "50mg", minPrice: 1500, maxPrice: 4000, availability: "limited" },
  { id: "d8", drugName: "Insulin Mixtard", genericName: "Human Insulin", dosage: "100IU/ml", minPrice: 15000, maxPrice: 25000, availability: "scarce" },
];
