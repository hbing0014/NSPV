"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { AlertTriangle, CheckCircle2, Compass, Loader2, Search, SlidersHorizontal } from "lucide-react";
import { Header } from "@/components/Header";
import { ApiRequestError, DiscoverProductsResponse, discoverProducts } from "@/lib/api";
import { useI18n } from "@/lib/i18n/LocaleProvider";

const categories = ["Kitchen & Dining", "Home & Kitchen", "Storage & Organization", "Cleaning Tools"];
const budgetOptions = [
  { label: "<50K RMB", value: 50000 },
  { label: "50K-100K RMB", value: 100000 },
  { label: "100K-200K RMB", value: 200000 }
];
const priceRanges = [
  { label: "$15-$25", min: 15, max: 25 },
  { label: "$25-$40", min: 25, max: 40 },
  { label: "$40-$60", min: 40, max: 60 }
];
const weightLimits = [
  { label: "<500g", value: 500 },
  { label: "500g-1kg", value: 1000 }
];

export default function Home() {
  const { t } = useI18n();
  const [category, setCategory] = useState("Kitchen & Dining");
  const [budget, setBudget] = useState(100000);
  const [riskPreference, setRiskPreference] = useState<"low" | "balanced" | "aggressive">("low");
  const [priceRange, setPriceRange] = useState(priceRanges[1]);
  const [weightLimit, setWeightLimit] = useState(500);
  const [excludeRedOcean, setExcludeRedOcean] = useState(true);
  const [excludeAmazonBasics, setExcludeAmazonBasics] = useState(true);
  const [excludeFragile, setExcludeFragile] = useState(true);
  const [excludeSeasonal, setExcludeSeasonal] = useState(true);
  const [lowMoqOnly, setLowMoqOnly] = useState(false);
  const [easyLaunchOnly, setEasyLaunchOnly] = useState(false);
  const [highMarginOnly, setHighMarginOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DiscoverProductsResponse | null>(null);
  const [error, setError] = useState<{ message: string; code?: string; status?: number } | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await discoverProducts({
        category,
        marketplace: "US",
        budget_rmb: budget,
        risk_preference: riskPreference,
        price_min: priceRange.min,
        price_max: priceRange.max,
        weight_limit_g: weightLimit,
        exclude_red_ocean: excludeRedOcean,
        exclude_amazon_basics: excludeAmazonBasics,
        exclude_fragile: excludeFragile,
        exclude_seasonal: excludeSeasonal,
        low_moq_only: lowMoqOnly,
        easy_launch_only: easyLaunchOnly,
        high_margin_only: highMarginOnly,
        min_launch_score: easyLaunchOnly ? 80 : undefined,
        min_npfs: undefined
      });
      setResult(response);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError({ message: err.message, code: err.code, status: err.status });
      } else {
        setError({
          message: err instanceof TypeError ? t.discover.error.connect : t.discover.error.failed,
          code: "CLIENT_ERROR"
        });
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 py-8">
        <section className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="py-4">
            <div className="text-sm font-medium text-accent">{t.discover.eyebrow}</div>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
              {t.discover.title}
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-ink/70">{t.discover.subtitle}</p>
            <div className="mt-6 flex flex-wrap gap-3">
              <a className="inline-flex items-center gap-2 bg-accent px-4 py-3 font-medium text-white" href="#discover-form">
                <Compass size={18} aria-hidden="true" />
                {t.discover.actions.discover}
              </a>
              <Link
                className="inline-flex items-center gap-2 border border-line bg-white px-4 py-3 font-medium text-ink"
                href="/validate"
              >
                <Search size={18} aria-hidden="true" />
                {t.discover.actions.validate}
              </Link>
            </div>
          </div>

          <form id="discover-form" onSubmit={onSubmit} className="border border-line bg-white p-5" aria-busy={loading}>
            <div className="grid gap-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <SelectField label={t.discover.fields.category} value={category} onChange={setCategory} options={categories} />
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">{t.discover.fields.budget}</span>
                  <select
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    value={budget}
                    onChange={(event) => setBudget(Number(event.target.value))}
                  >
                    {budgetOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">{t.discover.fields.risk}</span>
                  <select
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    value={riskPreference}
                    onChange={(event) => setRiskPreference(event.target.value as "low" | "balanced" | "aggressive")}
                  >
                    <option value="low">{t.discover.risk.low}</option>
                    <option value="balanced">{t.discover.risk.balanced}</option>
                    <option value="aggressive">{t.discover.risk.aggressive}</option>
                  </select>
                </label>
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">{t.discover.fields.price}</span>
                  <select
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    value={priceRange.label}
                    onChange={(event) => setPriceRange(priceRanges.find((item) => item.label === event.target.value) ?? priceRanges[1])}
                  >
                    {priceRanges.map((range) => (
                      <option key={range.label} value={range.label}>
                        {range.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">{t.discover.fields.weight}</span>
                  <select
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    value={weightLimit}
                    onChange={(event) => setWeightLimit(Number(event.target.value))}
                  >
                    {weightLimits.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="border border-line bg-field p-4">
                <div className="mb-3 flex items-center gap-2 text-sm font-medium text-ink">
                  <SlidersHorizontal size={17} aria-hidden="true" />
                  {t.discover.filters.title}
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <Check label={t.discover.filters.redOcean} checked={excludeRedOcean} onChange={setExcludeRedOcean} />
                  <Check label={t.discover.filters.amazonBasics} checked={excludeAmazonBasics} onChange={setExcludeAmazonBasics} />
                  <Check label={t.discover.filters.fragile} checked={excludeFragile} onChange={setExcludeFragile} />
                  <Check label={t.discover.filters.seasonal} checked={excludeSeasonal} onChange={setExcludeSeasonal} />
                  <Check label={t.discover.filters.lowMoq} checked={lowMoqOnly} onChange={setLowMoqOnly} />
                  <Check label={t.discover.filters.easyLaunch} checked={easyLaunchOnly} onChange={setEasyLaunchOnly} />
                  <Check label={t.discover.filters.highMargin} checked={highMarginOnly} onChange={setHighMarginOnly} />
                </div>
              </div>

              {error ? (
                <div className="border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert">
                  <div className="flex gap-3">
                    <AlertTriangle className="mt-0.5 shrink-0 text-red-600" size={18} aria-hidden="true" />
                    <div>
                      <div className="font-medium">{t.discover.error.title}</div>
                      <p className="mt-1 leading-6">{error.message}</p>
                      <div className="mt-2 flex gap-2 text-xs text-red-700/80">
                        {error.code ? <span>{error.code}</span> : null}
                        {error.status ? <span>HTTP {error.status}</span> : null}
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}

              {result ? (
                <div className="border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900" role="status">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="mt-0.5 shrink-0 text-emerald-700" size={18} aria-hidden="true" />
                    <div>
                      <div className="font-medium">
                        {t.discover.result.title.replace("{count}", String(result.total_recommendations))}
                      </div>
                      <p className="mt-1 leading-6">
                        {t.discover.result.meta
                          .replace("{scanned}", String(result.total_products_scanned))
                          .replace("{filtered}", String(result.total_products_filtered))}
                      </p>
                      {result.products[0] ? (
                        <div className="mt-3 text-sm font-medium text-emerald-950">
                          {result.products[0].product_name} · NPFS {result.products[0].npfs_score}
                        </div>
                      ) : null}
                    </div>
                  </div>
                </div>
              ) : null}

              <button
                className="flex items-center justify-center gap-2 bg-accent px-4 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                type="submit"
                disabled={loading}
              >
                {loading ? <Loader2 className="animate-spin" size={18} aria-hidden="true" /> : <Compass size={18} aria-hidden="true" />}
                {loading ? t.discover.actions.loading : t.discover.actions.discover}
              </button>
            </div>
          </form>
        </section>
      </main>
    </>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
}) {
  return (
    <label className="grid gap-2">
      <span className="text-sm font-medium text-ink">{label}</span>
      <select
        className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function Check({ label, checked, onChange }: { label: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center gap-3 text-sm text-ink">
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
      {label}
    </label>
  );
}
