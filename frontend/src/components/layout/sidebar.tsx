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
    if (route === "/data") return pathname === "/data";
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
          <Link href="/data" className="flex items-center gap-3 text-2xl font-black tracking-tighter" onClick={closeSidebar}>
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
            const isDisabled = item.disabled;

            const content = (
              <>
                <div className="relative shrink-0">
                  <NavIcon 
                    name={item.icon} 
                    className={cn(
                      active ? "text-neutral-950" : "text-neutral-500 group-hover/item:text-white",
                      isDisabled && "opacity-40 grayscale"
                    )} 
                  />
                  {isDisabled && (
                    <div className="absolute -right-1 -top-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-neutral-800 text-[8px] text-white ring-2 ring-neutral-950 transition-transform group-hover/item:scale-110">
                      <svg xmlns="http://www.w3.org/2000/svg" width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                      </svg>
                    </div>
                  )}
                </div>
                <div className="ml-4 hidden flex-col transition-opacity duration-500 group-hover/sidebar:flex">
                  <span className={cn(
                    "whitespace-nowrap text-sm font-bold tracking-tight",
                    active ? "text-neutral-950" : "text-neutral-400 group-hover/item:text-white",
                    isDisabled && "opacity-40"
                  )}>
                    {t(item.translationKey)}
                  </span>
                  {isDisabled && (
                    <span className="text-[10px] font-black uppercase tracking-widest text-white/40">
                      {t("common.comingSoon")}
                    </span>
                  )}
                </div>
              </>
            );

            if (isDisabled) {
              return (
                <div
                  key={item.key}
                  title={t("common.comingSoon")}
                  className="group/item relative flex h-12 w-12 cursor-not-allowed items-center justify-center rounded-2xl bg-transparent transition-all duration-500 hover:bg-neutral-900 group-hover/sidebar:w-48 group-hover/sidebar:justify-start group-hover/sidebar:px-5"
                >
                  {content}
                </div>
              );
            }

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
                {content}
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
