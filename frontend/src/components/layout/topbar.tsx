import { LanguageSwitcher } from "./language-switcher";

export function Topbar() {
  return (
    <header className="flex h-20 items-center justify-between bg-transparent">
      <div>
        <h1 className="text-2xl font-black tracking-tight text-neutral-900 uppercase">
          System Overview
        </h1>
        <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
          Live Intelligence Deck
        </p>
      </div>
      <div className="flex items-center gap-4">
        <div className="h-10 w-px bg-neutral-200" />
        <LanguageSwitcher />
      </div>
    </header>
  );
}
