import type { JobTrend, Salary } from "@/types/api";

export const salaries: Salary[] = [
  { id: "s1", role: "Software Engineer", sector: "Technology", avgSalary: 3500000, minSalary: 2000000, maxSalary: 6000000, experience: "Mid-level" },
  { id: "s2", role: "Accountant", sector: "Finance", avgSalary: 1800000, minSalary: 1200000, maxSalary: 3000000, experience: "Mid-level" },
  { id: "s3", role: "Nurse", sector: "Healthcare", avgSalary: 1200000, minSalary: 800000, maxSalary: 2000000, experience: "Mid-level" },
  { id: "s4", role: "Teacher", sector: "Education", avgSalary: 900000, minSalary: 600000, maxSalary: 1500000, experience: "Mid-level" },
  { id: "s5", role: "Marketing Manager", sector: "Marketing", avgSalary: 2800000, minSalary: 1800000, maxSalary: 4500000, experience: "Senior" },
  { id: "s6", role: "Civil Engineer", sector: "Construction", avgSalary: 2500000, minSalary: 1500000, maxSalary: 4000000, experience: "Mid-level" },
  { id: "s7", role: "Data Analyst", sector: "Technology", avgSalary: 2800000, minSalary: 1800000, maxSalary: 4500000, experience: "Mid-level" },
  { id: "s8", role: "Doctor", sector: "Healthcare", avgSalary: 4500000, minSalary: 3000000, maxSalary: 8000000, experience: "Senior" },
];

export const jobTrends: JobTrend[] = [
  { id: "j1", role: "Software Engineer", sector: "Technology", demand: "growing", openings: 1250, changePercent: 18.5 },
  { id: "j2", role: "Data Analyst", sector: "Technology", demand: "growing", openings: 680, changePercent: 24.3 },
  { id: "j3", role: "Digital Marketer", sector: "Marketing", demand: "growing", openings: 420, changePercent: 15.2 },
  { id: "j4", role: "Accountant", sector: "Finance", demand: "stable", openings: 350, changePercent: 2.1 },
  { id: "j5", role: "Nurse", sector: "Healthcare", demand: "growing", openings: 890, changePercent: 12.0 },
  { id: "j6", role: "Teacher", sector: "Education", demand: "stable", openings: 1100, changePercent: -1.5 },
  { id: "j7", role: "Civil Engineer", sector: "Construction", demand: "growing", openings: 310, changePercent: 8.7 },
  { id: "j8", role: "Bank Teller", sector: "Finance", demand: "declining", openings: 120, changePercent: -15.3 },
];
