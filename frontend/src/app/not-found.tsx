import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex h-screen flex-col items-center justify-center">
      <h1 className="text-6xl font-bold text-neutral-900">404</h1>
      <p className="mt-2 text-neutral-500">Page not found</p>
      <Link
        href="/"
        className="mt-6 rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-neutral-800"
      >
        Back to Dashboard
      </Link>
    </div>
  );
}
