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
    return pathname.startsWith(route);
  }

  return (
    <aside className="flex h-full w-56 flex-col border-r border-neutral-200 bg-white">
      <div className="flex h-14 items-center border-b border-neutral-200 px-5">
        <Link href="/" className="text-xl font-bold tracking-tight text-neutral-900">
          AQ
        </Link>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {NAV_ITEMS.map((item) => {
          const route = ROUTES[item.key];
          const active = isActive(route);

          return (
            <Link
              key={item.key}
              href={route}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-neutral-900 text-white"
                  : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900",
              )}
            >
              <NavIcon name={item.icon} />
              <span>{t(item.translationKey)}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
