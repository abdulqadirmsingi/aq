"use client";

import { NAV_ITEMS, ROUTES } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { NavIcon } from "./nav-icon";

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations();

  function isActive(route: string): boolean {
    if (route === "/") return pathname === "/";
    if (route === "/energy" && pathname.startsWith("/energy/monitoring")) {
      return false;
    }
    return pathname.startsWith(route);
  }

  return (
    <aside className="fixed bottom-6 left-6 top-6 z-50 flex w-20 flex-col items-center gap-8 rounded-[2.5rem] bg-neutral-950 py-10 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.5)] transition-all duration-500 hover:w-64 group/sidebar">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-neutral-950 group-hover/sidebar:w-48 group-hover/sidebar:justify-start group-hover/sidebar:px-6 transition-all duration-500 overflow-hidden ring-4 ring-neutral-800">
        <Link href="/" className="flex items-center gap-3 text-2xl font-black tracking-tighter">
          <span className="shrink-0">AQ</span>
          <span className="hidden opacity-0 group-hover/sidebar:block group-hover/sidebar:opacity-100 transition-opacity duration-700">DATA</span>
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
              className={cn(
                "group/item relative flex h-12 w-12 items-center justify-center rounded-2xl transition-all duration-500 overflow-hidden group-hover/sidebar:w-48 group-hover/sidebar:justify-start group-hover/sidebar:px-5",
                active
                  ? "bg-white text-neutral-950 shadow-[0_0_20px_rgba(255,255,255,0.3)]"
                  : "text-neutral-500 hover:bg-neutral-800 hover:text-white",
              )}
            >
              <div className="shrink-0 scale-110">
                <NavIcon name={item.icon} />
              </div>
              <span className={cn(
                "ml-4 hidden whitespace-nowrap text-sm font-bold tracking-tight opacity-0 transition-opacity duration-500 group-hover/sidebar:block group-hover/sidebar:opacity-100",
                active ? "text-neutral-950" : "text-neutral-400 group-hover/item:text-white"
              )}>
                {t(item.translationKey)}
              </span>
              
              {/* Active Indicator Dot */}
              {active && (
                <div className="absolute right-4 h-1.5 w-1.5 rounded-full bg-neutral-950 group-hover/sidebar:block hidden" />
              )}
            </Link>
          );
        })}
      </nav>
      
      {/* Decorative innovative element at bottom */}
      <div className="mt-auto flex h-1 w-8 rounded-full bg-neutral-800 group-hover/sidebar:w-32 transition-all duration-500" />
    </aside>
  );
}
