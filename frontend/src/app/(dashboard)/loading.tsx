import { CardSkeleton, TableSkeleton } from "@/components/ui/skeleton";

export default function DashboardLoading() {
  return (
    <div className="space-y-6">
      <div>
        <div className="mb-2 h-8 w-48 animate-pulse rounded bg-neutral-200" />
        <div className="h-4 w-64 animate-pulse rounded bg-neutral-100" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {Array.from({ length: 5 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
      <TableSkeleton rows={6} />
    </div>
  );
}
