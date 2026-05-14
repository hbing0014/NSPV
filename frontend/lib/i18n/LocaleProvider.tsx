"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { defaultLocale, getDictionary, isLocale, Locale } from "@/lib/i18n/dictionaries";

type LocaleContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: ReturnType<typeof getDictionary>;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({
  initialLocale,
  children
}: {
  initialLocale: Locale;
  children: React.ReactNode;
}) {
  const [locale, setLocaleState] = useState<Locale>(initialLocale);

  useEffect(() => {
    const saved = window.localStorage.getItem("nspv-locale");
    if (saved && isLocale(saved) && saved !== locale) {
      setLocaleState(saved);
    }
  }, []);

  function setLocale(nextLocale: Locale) {
    setLocaleState(nextLocale);
    window.localStorage.setItem("nspv-locale", nextLocale);
    document.cookie = `nspv-locale=${nextLocale}; path=/; max-age=31536000; SameSite=Lax`;
    document.documentElement.lang = nextLocale;
  }

  const value = useMemo(
    () => ({
      locale,
      setLocale,
      t: getDictionary(locale)
    }),
    [locale]
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useI18n() {
  const context = useContext(LocaleContext);
  if (!context) {
    return {
      locale: defaultLocale,
      setLocale: () => undefined,
      t: getDictionary(defaultLocale)
    };
  }
  return context;
}
