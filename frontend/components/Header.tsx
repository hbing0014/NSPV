"use client";

import Link from "next/link";
import { BarChart3 } from "lucide-react";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { useI18n } from "@/lib/i18n/LocaleProvider";

export function Header() {
  const { t } = useI18n();

  return (
    <header className="border-b border-line bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
        <Link href="/" className="flex items-center gap-3 font-semibold text-ink">
          <span className="flex h-9 w-9 items-center justify-center bg-accent text-white">
            <BarChart3 size={20} aria-hidden="true" />
          </span>
          <span>NSPV</span>
        </Link>
        <div className="flex items-center gap-5">
          <nav className="flex items-center gap-5 text-sm text-ink/70">
            <Link href="/">{t.nav.discover}</Link>
            <Link href="/validate">{t.nav.validate}</Link>
            <Link href="/reports">{t.nav.reports}</Link>
          </nav>
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  );
}
