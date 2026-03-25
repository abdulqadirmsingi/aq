"use client";

import { defaultLocale, locales, type Locale } from "@/i18n/config";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useEffect, useState, useTransition } from "react";

function getLocaleFromCookie(): Locale {
  if (typeof document === "undefined") return defaultLocale;
  const match = document.cookie.match(/(?:^|;\s*)locale=(\w+)/);
  return locales.includes(match?.[1] as Locale) ? (match![1] as Locale) : defaultLocale;
}

export function LanguageSwitcher() {
  const t = useTranslations("common");
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [locale, setLocale] = useState<Locale>(defaultLocale);

  useEffect(() => {
    setLocale(getLocaleFromCookie());
  }, []);

  function handleChange(newLocale: Locale) {
    document.cookie = `locale=${newLocale};path=/;max-age=31536000`;
    setLocale(newLocale);
    startTransition(() => {
      router.refresh();
    });
  }

  return (
    <div className="flex items-center gap-1.5">
      {locales.map((loc) => (
        <button
          key={loc}
          onClick={() => handleChange(loc)}
          disabled={isPending}
          className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
            locale === loc
              ? "bg-neutral-900 text-white"
              : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
          }`}
        >
          {loc === "en" ? t("english") : t("swahili")}
        </button>
      ))}
    </div>
  );
}
