"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Compass, Loader2, Search, SlidersHorizontal } from "lucide-react";
import { Header } from "@/components/Header";
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

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (loading) {
      return;
    }

    setLoading(true);
    const params = new URLSearchParams({
      category,
      budget_max: String(budget),
      risk_preference: riskPreference,
      price_min: String(priceRange.min),
      price_max: String(priceRange.max),
      weight_limit_g: String(weightLimit),
      exclude_red_ocean: String(excludeRedOcean),
      exclude_amazon_basics: String(excludeAmazonBasics),
      exclude_fragile: String(excludeFragile),
      exclude_seasonal: String(excludeSeasonal),
      low_moq_only: String(lowMoqOnly),
      easy_launch_only: String(easyLaunchOnly),
      high_margin_only: String(highMarginOnly),
      sort: "highest_npfs"
    });
    window.location.assign(`/radar?${params.toString()}`);
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
              <button
                className="inline-flex items-center gap-2 bg-accent px-4 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                type="submit"
                form="discover-form"
                disabled={loading}
              >
                <Compass size={18} aria-hidden="true" />
                {loading ? t.discover.actions.loading : t.discover.actions.discover}
              </button>
              <Link
                className="inline-flex items-center gap-2 border border-line bg-white px-4 py-3 font-medium text-ink"
                href="/validate"
              >
                <Search size={18} aria-hidden="true" />
                {t.discover.actions.validate}
              </Link>
            </div>
          </div>

          <form
            id="discover-form"
            action="/radar"
            method="get"
            onSubmit={onSubmit}
            className="border border-line bg-white p-5"
            aria-busy={loading}
          >
            <div className="grid gap-4">
              <input type="hidden" name="price_min" value={priceRange.min} />
              <input type="hidden" name="price_max" value={priceRange.max} />
              <input type="hidden" name="risk_preference" value={riskPreference} />
              <input type="hidden" name="weight_limit_g" value={weightLimit} />
              <input type="hidden" name="exclude_red_ocean" value={String(excludeRedOcean)} />
              <input type="hidden" name="exclude_amazon_basics" value={String(excludeAmazonBasics)} />
              <input type="hidden" name="exclude_fragile" value={String(excludeFragile)} />
              <input type="hidden" name="exclude_seasonal" value={String(excludeSeasonal)} />
              <input type="hidden" name="low_moq_only" value={String(lowMoqOnly)} />
              <input type="hidden" name="easy_launch_only" value={String(easyLaunchOnly)} />
              <input type="hidden" name="high_margin_only" value={String(highMarginOnly)} />
              <input type="hidden" name="sort" value="highest_npfs" />
              <div className="grid gap-4 sm:grid-cols-2">
                <SelectField label={t.discover.fields.category} name="category" value={category} onChange={setCategory} options={categories} />
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">{t.discover.fields.budget}</span>
                  <select
                    name="budget_max"
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
  name,
  value,
  onChange,
  options
}: {
  label: string;
  name?: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
}) {
  return (
    <label className="grid gap-2">
      <span className="text-sm font-medium text-ink">{label}</span>
      <select
        name={name}
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
