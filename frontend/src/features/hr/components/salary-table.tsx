"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import { formatNumber } from "@/lib/utils";
import type { Salary } from "@/types/api";
import { useTranslations } from "next-intl";

interface SalaryTableProps {
  data: Salary[];
}

export function SalaryTable({ data }: SalaryTableProps) {
  const t = useTranslations();

  const columns = [
    {
      key: "role",
      header: t("hr.role"),
      render: (item: Salary) => <span className="font-medium">{item.role}</span>,
    },
    {
      key: "sector",
      header: t("hr.sector"),
      render: (item: Salary) => <Badge>{item.sector}</Badge>,
    },
    {
      key: "avg",
      header: t("hr.avgSalary"),
      render: (item: Salary) => (
        <span className="font-medium">{formatNumber(item.avgSalary)}</span>
      ),
    },
    {
      key: "range",
      header: t("medicine.priceRange"),
      render: (item: Salary) => (
        <span className="text-neutral-500">
          {formatNumber(item.minSalary)} – {formatNumber(item.maxSalary)}
        </span>
      ),
    },
    {
      key: "experience",
      header: t("hr.experience"),
      render: (item: Salary) => item.experience,
    },
  ];

  return (
    <div>
      <SectionHeader title={t("hr.salaries")} description={t("hr.salaryDescription")} />
      <DataTable columns={columns} data={data} keyExtractor={(item) => item.id} />
    </div>
  );
}
