import { CardSkeleton } from "@/components/ui/skeleton";

export default function GlobalLoading() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="w-full max-w-md space-y-4 p-6">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    </div>
  );
}
