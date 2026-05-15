"use client";

import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AlertTriangle, Loader2, Radar, SlidersHorizontal } from "lucide-react";
import { Header } from "@/components/Header";
import { ProductOpportunityCard } from "@/components/ProductOpportunityCard";
import { ApiRequestError, RadarProductsResponse, getRadarProducts } from "@/lib/api";
import { useI18n } from "@/lib/i18n/LocaleProvider";

const categories = ["", "Kitchen & Dining", "Home & Kitchen", "Storage & Organization"];
const riskLevels = ["", "low", "medium", "high"];
const sortOptions = ["highest_npfs", "lowest_risk", "lowest_budget", "highest_profit", "easiest_launch"] as const;

export default function RadarPage() {
  const { t } = useI18n();
  const searchParams = useSearchParams();
  const [category, setCategory] = useState(searchParams.get("category") ?? "");
  const [riskLevel, setRiskLevel] = useState("");
  const [budgetMax, setBudgetMax] = useState(Number(searchParams.get("budget_max") ?? 100000));
  const [priceMin, setPriceMin] = useState(Number(searchParams.get("price_min") ?? 15));
  const [priceMax, setPriceMax] = useState(Number(searchParams.get("price_max") ?? 60));
  const initialSort = searchParams.get("sort");
  const [sort, setSort] = useState<(typeof sortOptions)[number]>(
    sortOptions.includes(initialSort as (typeof sortOptions)[number])
      ? (initialSort as (typeof sortOptions)[number])
      : "highest_npfs"
  );
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<RadarProductsResponse | null>(null);
  const [error, setError] = useState<{ message: string; code?: string; status?: number } | null>(null);

  useEffect(() => {
    void loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadProducts() {
    setLoading(true);
    setError(null);

    try {
      const response = await getRadarProducts({
        category: category || undefined,
        risk_level: riskLevel || undefined,
        budget_max: budgetMax,
        price_min: priceMin,
        price_max: priceMax,
        sort,
        limit: 50
      });
      setResult(response);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError({ message: err.message, code: err.code, status: err.status });
      } else {
        setError({
          message: err instanceof TypeError ? t.radar.error.connect : t.radar.error.failed,
          code: "CLIENT_ERROR"
        });
      }
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadProducts();
  }

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 py-8">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="text-sm font-medium text-accent">{t.radar.eyebrow}</div>
            <h1 className="mt-2 text-3xl font-semibold text-ink">{t.radar.title}</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/65">{t.radar.subtitle}</p>
          </div>
          <div className="border border-line bg-white px-4 py-3 text-sm text-ink/70">
            {t.radar.summary.replace("{count}", String(result?.total ?? 0))}
          </div>
        </div>

        <form onSubmit={onSubmit} className="mb-6 border border-line bg-white p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-medium text-ink">
            <SlidersHorizontal size={17} aria-hidden="true" />
            {t.radar.filters.title}
          </div>
          <div className="grid gap-4 md:grid-cols-6">
            <Select label={t.radar.filters.category} value={category} onChange={setCategory} options={categories} fallback={t.radar.filters.all} />
            <Select label={t.radar.filters.risk} value={riskLevel} onChange={setRiskLevel} options={riskLevels} fallback={t.radar.filters.all} />
            <NumberField label={t.radar.filters.budgetMax} value={budgetMax} onChange={setBudgetMax} />
            <NumberField label={t.radar.filters.priceMin} value={priceMin} onChange={setPriceMin} />
            <NumberField label={t.radar.filters.priceMax} value={priceMax} onChange={setPriceMax} />
            <label className="grid gap-2">
              <span className="text-sm font-medium text-ink">{t.radar.filters.sort}</span>
              <select
                className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                value={sort}
                onChange={(event) => setSort(event.target.value as (typeof sortOptions)[number])}
              >
                {sortOptions.map((option) => (
                  <option key={option} value={option}>
                    {t.radar.sort[option]}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <button className="mt-4 inline-flex items-center gap-2 bg-accent px-4 py-3 font-medium text-white" type="submit">
            <Radar size={18} aria-hidden="true" />
            {t.radar.actions.apply}
          </button>
        </form>

        {error ? (
          <div className="border border-red-200 bg-red-50 p-4 text-sm text-red-800" role="alert">
            <div className="flex gap-3">
              <AlertTriangle className="mt-0.5 shrink-0 text-red-600" size={18} aria-hidden="true" />
              <div>
                <div className="font-medium">{t.radar.error.title}</div>
                <p className="mt-1 leading-6">{error.message}</p>
              </div>
            </div>
          </div>
        ) : null}

        {loading ? (
          <div className="flex items-center gap-2 border border-line bg-white p-6 text-sm text-ink/70">
            <Loader2 className="animate-spin" size={18} aria-hidden="true" />
            {t.radar.loading}
          </div>
        ) : null}

        {!loading && result && !result.products.length ? (
          <div className="border border-line bg-white p-8 text-sm text-ink/60">{t.radar.empty}</div>
        ) : null}

        <div className="grid gap-4">
          {result?.products.map((product) => (
            <ProductOpportunityCard key={product.product_opportunity_id} product={product} labels={t.discover.card} />
          ))}
        </div>
      </main>
    </>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
  fallback
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
  fallback: string;
}) {
  return (
    <label className="grid gap-2">
      <span className="text-sm font-medium text-ink">{label}</span>
      <select className="border border-line bg-field px-3 py-3 outline-none focus:border-accent" value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option || "all"} value={option}>
            {option || fallback}
          </option>
        ))}
      </select>
    </label>
  );
}

function NumberField({ label, value, onChange }: { label: string; value: number; onChange: (value: number) => void }) {
  return (
    <label className="grid gap-2">
      <span className="text-sm font-medium text-ink">{label}</span>
      <input
        className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
        min={0}
        type="number"
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}
