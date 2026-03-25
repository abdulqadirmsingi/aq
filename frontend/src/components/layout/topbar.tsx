import { LanguageSwitcher } from "./language-switcher";

export function Topbar() {
  return (
    <header className="flex h-14 items-center justify-between border-b border-neutral-200 bg-white px-6">
      <div />
      <LanguageSwitcher />
    </header>
  );
}
