import Link from "next/link";
import { Logo } from "@/components/ui/logo";

export function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-neutral-50/90 backdrop-blur-md border-b-2 border-neutral-900">
      <div className="flex items-center gap-3">
        <Logo className="h-10 w-10 text-neutral-900" accentColor="text-emerald-500" />
        <span className="font-bold tracking-widest text-sm uppercase text-neutral-900">Data Lab</span>
      </div>
      
      <div className="hidden md:flex items-center gap-8 text-xs font-bold tracking-widest uppercase text-neutral-600">
        <a href="#data" className="hover:text-neutral-900 transition-colors">Available Data</a>
        <a href="#roadmap" className="hover:text-neutral-900 transition-colors">Roadmap</a>
      </div>

      <Link 
        href="/data" 
        className="group relative inline-flex items-center justify-center gap-2 border-2 border-neutral-900 bg-white px-6 py-2.5 text-xs font-bold uppercase tracking-widest text-neutral-900 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none"
      >
        Enter Dashboard
      </Link>
    </nav>
  );
}