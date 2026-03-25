import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return <div className={cn("animate-pulse rounded bg-neutral-200", className)} />;
}

export function CardSkeleton() {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-5">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="mt-3 h-8 w-32" />
      <Skeleton className="mt-2 h-3 w-16" />
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="overflow-hidden rounded-lg border border-neutral-200">
      <div className="bg-neutral-50 px-4 py-3">
        <Skeleton className="h-4 w-full" />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="border-t border-neutral-100 px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </div>
      ))}
    </div>
  );
}
