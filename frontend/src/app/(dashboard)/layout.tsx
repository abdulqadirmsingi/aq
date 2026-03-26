import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen bg-neutral-50 selection:bg-neutral-900 selection:text-white">
      <Sidebar />
      <div className="flex flex-col px-6 transition-all duration-500 lg:pl-36 lg:pr-8">
        <Topbar />
        <main className="flex-1 py-10">{children}</main>
      </div>
    </div>
  );
}
