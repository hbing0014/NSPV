"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { Header } from "@/components/Header";
import { analyzeKeyword } from "@/lib/api";

const categories = ["Kitchen & Dining", "Home & Kitchen", "Storage & Organization", "Tools & Home Improvement"];

export default function Home() {
  const router = useRouter();
  const [keyword, setKeyword] = useState("sink organizer");
  const [marketplace, setMarketplace] = useState("US");
  const [category, setCategory] = useState("Kitchen & Dining");
  const [budget, setBudget] = useState(100000);
  const [priceMin, setPriceMin] = useState(20);
  const [priceMax, setPriceMax] = useState(40);
  const [excludeRedOcean, setExcludeRedOcean] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runAnalyze() {
    setLoading(true);
    setError("");

    try {
      const report = await analyzeKeyword({
        keyword,
        marketplace,
        category,
        budget_rmb: budget,
        target_price_min: priceMin,
        target_price_max: priceMax,
        exclude_red_ocean: excludeRedOcean
      });
      router.push(`/reports/${report.report_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analyze failed");
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runAnalyze();
  }

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 py-8">
        <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <div className="text-sm font-medium text-accent">New Seller Product Validator</div>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
              Amazon 新店选品风险判断
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-ink/70">
              输入一个美国站关键词，系统会分析首页 Top20 商品结构，生成 NSFS 评分、红海预警和进入建议。
            </p>
          </div>

          <form onSubmit={onSubmit} className="border border-line bg-white p-5">
            <div className="grid gap-4">
              <label className="grid gap-2">
                <span className="text-sm font-medium text-ink">Keyword</span>
                <input
                  className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                  value={keyword}
                  onChange={(event) => setKeyword(event.target.value)}
                  required
                />
              </label>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">Marketplace</span>
                  <select
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    value={marketplace}
                    onChange={(event) => setMarketplace(event.target.value)}
                  >
                    <option value="US">US</option>
                  </select>
                </label>
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">Category</span>
                  <select
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                  >
                    {categories.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <label className="grid gap-2">
                <span className="text-sm font-medium text-ink">Budget RMB</span>
                <input
                  className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                  type="number"
                  min={1}
                  value={budget}
                  onChange={(event) => setBudget(Number(event.target.value))}
                  required
                />
              </label>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">Target Price Min</span>
                  <input
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    type="number"
                    min={1}
                    value={priceMin}
                    onChange={(event) => setPriceMin(Number(event.target.value))}
                    required
                  />
                </label>
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">Target Price Max</span>
                  <input
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    type="number"
                    min={1}
                    value={priceMax}
                    onChange={(event) => setPriceMax(Number(event.target.value))}
                    required
                  />
                </label>
              </div>

              <label className="flex items-center gap-3 text-sm text-ink">
                <input
                  type="checkbox"
                  checked={excludeRedOcean}
                  onChange={(event) => setExcludeRedOcean(event.target.checked)}
                />
                Exclude red ocean by default
              </label>

              {error ? (
                <div className="border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {error}
                </div>
              ) : null}

              <button
                className="flex items-center justify-center gap-2 bg-accent px-4 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                type="button"
                disabled={loading}
                onClick={runAnalyze}
              >
                <Search size={18} aria-hidden="true" />
                {loading ? "Analyzing..." : "Analyze"}
              </button>
            </div>
          </form>
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-4">
          <Signal label="Demand" text="Search volume and estimated monthly sales" />
          <Signal label="Competition" text="Review structure, ads, brand concentration" />
          <Signal label="Profit" text="Margin, ROI and break-even ACOS" />
          <Signal label="Opportunity" text="Rating gaps and upgrade potential" />
        </section>
      </main>
    </>
  );
}

function Signal({ label, text }: { label: string; text: string }) {
  return (
    <div className="border border-line bg-white p-4">
      <div className="font-semibold text-ink">{label}</div>
      <div className="mt-2 text-sm leading-6 text-ink/65">{text}</div>
    </div>
  );
}
