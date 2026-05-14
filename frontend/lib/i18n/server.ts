import { cookies } from "next/headers";
import { defaultLocale, isLocale, Locale } from "@/lib/i18n/dictionaries";

export async function getServerLocale(): Promise<Locale> {
  const cookieStore = await cookies();
  const value = cookieStore.get("nspv-locale")?.value;
  return isLocale(value) ? value : defaultLocale;
}
