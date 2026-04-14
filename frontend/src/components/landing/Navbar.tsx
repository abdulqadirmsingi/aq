"use client";

import Link from "next/link";
import { useState } from "react";
import { Logo } from "@/components/ui/logo";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { href: "#data", label: "Available Data", code: "01" },
] as const;

export function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="fixed inset-x-0 top-0 z-50 pointer-events-none">
      <div className="mx-auto flex max-w-5xl justify-center px-4 pt-4 sm:pt-5">
        <nav
          className={cn(
            "pointer-events-auto relative flex w-full flex-wrap items-center justify-between gap-3 overflow-hidden rounded-2xl border-2 border-neutral-900 bg-neutral-50/90 px-3 py-2.5 shadow-[6px_6px_0_0_#171717] backdrop-blur-md sm:flex-nowrap sm:gap-4 sm:px-4 sm:py-3"
          )}
          aria-label="Primary"
        >
          <div
            className="pointer-events-none absolute inset-x-4 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-80"
            aria-hidden
          />

          <Link
            href="/"
            className="group flex min-w-0 items-center gap-2.5 sm:gap-3"
            onClick={() => setMenuOpen(false)}
          >
            <span className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border-2 border-neutral-900 bg-white shadow-[2px_2px_0_0_#171717] transition-transform group-hover:-translate-y-0.5 sm:h-10 sm:w-10">
              <Logo className="h-6 w-6 text-neutral-900 sm:h-7 sm:w-7" accentColor="text-emerald-500" />
            </span>
            <span className="flex min-w-0 flex-col leading-none">
              <span className="truncate text-xs font-black uppercase tracking-[0.2em] text-neutral-900 sm:text-sm">
                Data Lab
              </span>
            </span>
          </Link>

          <div className="hidden md:flex md:flex-1 md:items-center md:justify-center md:gap-1">
            {NAV_LINKS.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="group flex items-center gap-2 rounded-xl px-3 py-2 font-mono text-[11px] uppercase tracking-wider text-neutral-600 transition-colors hover:bg-neutral-900 hover:text-white"
              >
                <span className="tabular-nums text-emerald-600 group-hover:text-emerald-300">{item.code}</span>
                <span className="hidden lg:inline text-neutral-400 group-hover:text-neutral-500">/</span>
                <span className="font-sans text-xs font-bold tracking-wide">{item.label}</span>
              </a>
            ))}
          </div>

          <div className="flex shrink-0 items-center gap-2">
            <Link
              href="/data"
              className="inline-flex items-center justify-center gap-2 rounded-xl border-2 border-neutral-900 bg-neutral-900 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white shadow-[3px_3px_0_0_rgba(16,185,129,0.35)] transition-all hover:translate-x-px hover:translate-y-px hover:bg-neutral-800 hover:shadow-none sm:px-4 sm:text-[11px]"
              onClick={() => setMenuOpen(false)}
            >
              <span>View Data</span>
              <svg className="h-3.5 w-3.5 text-emerald-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>

            <button
              type="button"
              className="flex h-10 w-10 items-center justify-center rounded-xl border-2 border-neutral-900 bg-white text-neutral-900 shadow-[2px_2px_0_0_#171717] transition-all hover:translate-x-px hover:translate-y-px hover:shadow-none md:hidden"
              aria-expanded={menuOpen}
              aria-controls="mobile-nav"
              onClick={() => setMenuOpen((o) => !o)}
            >
              <span className="sr-only">{menuOpen ? "Close menu" : "Open menu"}</span>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
                {menuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>

          <div
            id="mobile-nav"
            className={cn(
              "basis-full overflow-hidden transition-[max-height,opacity] duration-300 ease-out md:hidden",
              menuOpen ? "max-h-40 opacity-100" : "max-h-0 opacity-0"
            )}
          >
            <div className="flex flex-col gap-1 border-t-2 border-neutral-900/10 pt-3">
              {NAV_LINKS.map((item) => (
                <a
                  key={item.href}
                  href={item.href}
                  className="flex items-center gap-3 rounded-xl px-3 py-2.5 font-mono text-[11px] uppercase tracking-wider text-neutral-700 hover:bg-neutral-900 hover:text-white"
                  onClick={() => setMenuOpen(false)}
                >
                  <span className="tabular-nums text-emerald-600">{item.code}</span>
                  <span className="font-sans text-xs font-bold tracking-wide">{item.label}</span>
                </a>
              ))}
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
}
