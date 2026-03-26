"use client";

import { useUIStore } from "@/store/ui";
import { LanguageSwitcher } from "./language-switcher";

export function Topbar() {
  const { toggleSidebar } = useUIStore();

  return (
    <header className="flex h-20 items-center justify-between bg-transparent">
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleSidebar}
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-white shadow-sm ring-1 ring-neutral-200 lg:hidden"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        <div>
          <h1 className="text-xl font-black tracking-tight text-neutral-900 uppercase sm:text-2xl">
            System Overview
          </h1>
          <p className="text-[10px] font-bold tracking-widest text-neutral-400 uppercase sm:text-xs">
            Live Intelligence Deck
          </p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="hidden h-10 w-px bg-neutral-200 sm:block" />
        <LanguageSwitcher />
      </div>
    </header>
  );
}
