"use client";

import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/ui/data-table";
import { SectionHeader } from "@/components/ui/section-header";
import type { EwuraFuelRunLogPage, EwuraFuelRunLogRead, EwuraFuelRunPage, EwuraFuelRunRead } from "@/types/api";
import { useTranslations } from "next-intl";

interface MonitoringSectionProps {
  runs: EwuraFuelRunPage;
  runLogs: EwuraFuelRunLogPage | null;
}

function getRunBadgeVariant(status: string): "default" | "success" | "warning" | "danger" {
  const normalized = status.toLowerCase();

  if (normalized === "success" || normalized === "completed") return "success";
  if (normalized === "running" || normalized === "queued") return "warning";
  if (normalized === "failed" || normalized === "error") return "danger";
  return "default";
}

export function MonitoringSection({ runs, runLogs }: MonitoringSectionProps) {
  const t = useTranslations();

  const runColumns = [
    {
      key: "status",
      header: t("energy.status"),
      render: (item: EwuraFuelRunRead) => (
        <Badge variant={getRunBadgeVariant(item.status)}>{item.status}</Badge>
      ),
    },
    {
      key: "scraper",
      header: t("energy.scraper"),
      render: (item: EwuraFuelRunRead) => item.scraper_name,
    },
    {
      key: "trigger",
      header: t("energy.trigger"),
      render: (item: EwuraFuelRunRead) => item.trigger_type,
    },
    {
      key: "records",
      header: t("energy.recordsInserted"),
      render: (item: EwuraFuelRunRead) => String(item.records_inserted),
    },
  ];

  const logColumns = [
    {
      key: "level",
      header: t("energy.level"),
      render: (item: EwuraFuelRunLogRead) => (
        <Badge variant={item.level.toLowerCase() === "error" ? "danger" : "default"}>
          {item.level}
        </Badge>
      ),
    },
    {
      key: "event",
      header: t("energy.eventType"),
      render: (item: EwuraFuelRunLogRead) => item.event_type,
    },
    {
      key: "message",
      header: t("energy.message"),
      render: (item: EwuraFuelRunLogRead) => item.message,
      className: "max-w-[28rem]",
    },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader
        title={t("energy.monitoring")}
        description={t("energy.monitoringDescription")}
      />
      <DataTable
        columns={runColumns}
        data={runs.items}
        keyExtractor={(item) => item.id}
        emptyMessage={t("common.noData")}
      />
      {runLogs ? (
        <DataTable
          columns={logColumns}
          data={runLogs.items}
          keyExtractor={(item) => item.id}
          emptyMessage={t("common.noData")}
        />
      ) : null}
    </div>
  );
}
