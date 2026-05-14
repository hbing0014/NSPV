"use client";

import { Globe2 } from "lucide-react";
import { Locale } from "@/lib/i18n/dictionaries";
import { useI18n } from "@/lib/i18n/LocaleProvider";

const options: { value: Locale; label: string }[] = [
  { value: "zh-CN", label: "中文" },
  { value: "en", label: "English" }
];

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();

  return (
    <label className="flex items-center gap-2 text-sm text-ink/70">
      <Globe2 size={16} aria-hidden="true" />
      <span className="sr-only">{t.language.label}</span>
      <select
        className="border border-line bg-field px-2 py-1 outline-none focus:border-accent"
        value={locale}
        onChange={(event) => setLocale(event.target.value as Locale)}
        aria-label={t.language.label}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
