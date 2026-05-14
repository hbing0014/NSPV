import Link from "next/link";
import { Compass, Search, TrendingUp } from "lucide-react";
import { Header } from "@/components/Header";
import { getDictionary } from "@/lib/i18n/dictionaries";
import { getServerLocale } from "@/lib/i18n/server";

const categories = ["Kitchen & Dining", "Home & Kitchen", "Storage & Organization", "Cleaning Tools"];

export default async function Home() {
  const locale = await getServerLocale();
  const t = getDictionary(locale);

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 py-8">
        <section className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="py-4">
            <div className="text-sm font-medium text-accent">{t.discover.eyebrow}</div>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
              {t.discover.title}
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-ink/70">{t.discover.subtitle}</p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link className="inline-flex items-center gap-2 bg-accent px-4 py-3 font-medium text-white" href="/radar">
                <Compass size={18} aria-hidden="true" />
                {t.discover.actions.discover}
              </Link>
              <Link
                className="inline-flex items-center gap-2 border border-line bg-white px-4 py-3 font-medium text-ink"
                href="/validate"
              >
                <Search size={18} aria-hidden="true" />
                {t.discover.actions.validate}
              </Link>
            </div>
          </div>

          <div className="border border-line bg-white p-5">
            <div className="flex items-center gap-2 text-sm font-medium text-ink">
              <TrendingUp size={18} aria-hidden="true" />
              {t.discover.preview.title}
            </div>
            <div className="mt-4 grid gap-3">
              {categories.map((category) => (
                <div key={category} className="flex items-center justify-between border border-line bg-field px-3 py-3">
                  <span className="font-medium text-ink">{category}</span>
                  <span className="text-sm text-ink/60">{t.discover.preview.status}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
