"use client";

import { useTranslations } from "next-intl";

interface ErrorPageProps {
  reset: () => void;
}

export default function GlobalError({ reset }: ErrorPageProps) {
  const t = useTranslations("common");

  return (
    <div className="flex h-screen flex-col items-center justify-center">
      <h1 className="text-2xl font-bold text-neutral-900">{t("error")}</h1>
      <button
        onClick={reset}
        className="mt-6 rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-neutral-800"
      >
        {t("retry")}
      </button>
    </div>
  );
}
