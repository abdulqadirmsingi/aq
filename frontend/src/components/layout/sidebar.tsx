"use client";

import { useUIStore } from "@/store/ui";
import { NAV_ITEMS, ROUTES } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { NavIcon } from "./nav-icon";

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations();
  const { isSidebarOpen, closeSidebar } = useUIStore();

  function isActive(route: string): boolean {
    if (route === "/") return pathname === "/";
    return pathname.startsWith(route);
  }

  return (
    <>
      {/* Mobile Overlay */}
      <div 
        className={cn(
          "fixed inset-0 z-[60] bg-neutral-950/20 backdrop-blur-sm transition-opacity duration-300 lg:hidden",
          isSidebarOpen ? "opacity-100" : "pointer-events-none opacity-0"
        )}
        onClick={closeSidebar}
      />

      <aside 
        className={cn(
          "fixed left-6 top-6 bottom-6 z-[70] flex flex-col items-center gap-8 rounded-[2.5rem] bg-neutral-950 py-10 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.5)] transition-all duration-500 group/sidebar",
          // Desktop behavior
          "lg:w-20 lg:hover:w-64",
          // Mobile behavior
          isSidebarOpen ? "translate-x-0 w-64" : "-translate-x-[calc(100%+24px)] lg:translate-x-0"
        )}
      >
        {/* Mobile Close Button */}
        <button 
          onClick={closeSidebar}
          className="absolute right-4 top-4 p-2 text-neutral-400 hover:text-white lg:hidden"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-neutral-950 group-hover/sidebar:w-48 group-hover/sidebar:justify-start group-hover/sidebar:px-6 transition-all duration-500 overflow-hidden ring-4 ring-neutral-800">
          <Link href="/" className="flex items-center gap-3 text-2xl font-black tracking-tighter" onClick={closeSidebar}>
            {/* Innovative Logo */}
            <div className="relative flex shrink-0 items-center justify-center">
               <span className="relative z-10">AQ</span>
               <div className="absolute -inset-1 rounded-lg bg-neutral-950 opacity-0 group-hover/sidebar:opacity-10 transition-opacity" />
            </div>
            <span className="hidden opacity-0 group-hover/sidebar:block group-hover/sidebar:opacity-100 transition-opacity duration-700 text-xs tracking-[0.2em] font-light">INTELLIGENCE</span>
          </Link>
        </div>

        <nav className="flex w-full flex-col items-center gap-4 px-3">
          {NAV_ITEMS.map((item) => {
            const route = ROUTES[item.key];
            const active = isActive(route);

            return (
              <Link
                key={item.key}
                href={route}
                onClick={closeSidebar}
                className={cn(
                  "group/item relative flex h-12 w-12 items-center justify-center rounded-2xl transition-all duration-500 overflow-hidden group-hover/sidebar:w-48 group-hover/sidebar:justify-start group-hover/sidebar:px-5",
                  active
                    ? "bg-white text-neutral-950 shadow-[0_8px_16px_rgba(255,255,255,0.1)]"
                    : "text-neutral-500 hover:bg-neutral-800 hover:text-white",
                )}
              >
                <div className="shrink-0">
                  <NavIcon name={item.icon} className={cn(active ? "text-neutral-950" : "text-neutral-500 group-hover/item:text-white")} />
                </div>
                <span className={cn(
                  "ml-4 hidden whitespace-nowrap text-sm font-bold tracking-tight opacity-0 transition-opacity duration-500 group-hover/sidebar:block group-hover/sidebar:opacity-100",
                  active ? "text-neutral-950" : "text-neutral-400 group-hover/item:text-white"
                )}>
                  {t(item.translationKey)}
                </span>
              </Link>
            );
          })}
        </nav>
        
        {/* Decorative innovative element at bottom */}
        <div className="mt-auto flex h-1 w-8 rounded-full bg-neutral-800 group-hover/sidebar:w-32 transition-all duration-500" />
      </aside>
    </>
  );
}
