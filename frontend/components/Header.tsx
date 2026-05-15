"use client";

import { BarChart3 } from "lucide-react";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { AppHeader, AppHeaderActions, AppHeaderInner, AppLogo, AppNav, AppNavLink } from "@/components/ui/header";
import { useI18n } from "@/lib/i18n/LocaleProvider";

export function Header() {
  const { t } = useI18n();

  return (
    <AppHeader>
      <AppHeaderInner>
        <AppLogo icon={<BarChart3 size={20} aria-hidden="true" />}>NSPV</AppLogo>
        <AppHeaderActions>
          <AppNav>
            <AppNavLink href="/">{t.nav.discover}</AppNavLink>
            <AppNavLink href="/validate">{t.nav.validate}</AppNavLink>
            <AppNavLink href="/reports">{t.nav.reports}</AppNavLink>
          </AppNav>
          <LanguageSwitcher />
        </AppHeaderActions>
      </AppHeaderInner>
    </AppHeader>
  );
}
