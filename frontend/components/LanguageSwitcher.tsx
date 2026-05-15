"use client";

import { Globe2 } from "lucide-react";
import { Select } from "@/components/ui/select";
import { Locale } from "@/lib/i18n/dictionaries";
import { useI18n } from "@/lib/i18n/LocaleProvider";

const options: { value: Locale; label: string }[] = [
  { value: "zh-CN", label: "中文" },
  { value: "en", label: "English" }
];

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();

  return (
    <label className="flex items-center gap-2 text-sm text-muted-foreground">
      <Globe2 className="h-4 w-4" aria-hidden="true" />
      <span className="sr-only">{t.language.label}</span>
      <Select
        className="h-9 w-[118px] bg-card py-1 pl-2 text-xs"
        value={locale}
        onChange={(event) => setLocale(event.target.value as Locale)}
        aria-label={t.language.label}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
    </label>
  );
}
