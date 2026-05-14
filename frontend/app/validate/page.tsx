"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AlertTriangle, FolderOpen, Loader2, RotateCcw, Search } from "lucide-react";
import { Header } from "@/components/Header";
import { ApiRequestError, Project, analyzeKeyword, getProjects } from "@/lib/api";
import { useI18n } from "@/lib/i18n/LocaleProvider";

const categories = ["Kitchen & Dining", "Home & Kitchen", "Storage & Organization", "Tools & Home Improvement"];

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { locale, t } = useI18n();
  const [keyword, setKeyword] = useState(searchParams.get("keyword") ?? "sink organizer");
  const [marketplace, setMarketplace] = useState("US");
  const [category, setCategory] = useState(searchParams.get("category") ?? "Kitchen & Dining");
  const [budget, setBudget] = useState(Number(searchParams.get("budget_rmb") ?? 100000));
  const [priceMin, setPriceMin] = useState(Number(searchParams.get("target_price_min") ?? 20));
  const [priceMax, setPriceMax] = useState(Number(searchParams.get("target_price_max") ?? 40));
  const productOpportunityId = Number(searchParams.get("product_opportunity_id") ?? 0) || undefined;
  const [excludeRedOcean, setExcludeRedOcean] = useState(true);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectError, setProjectError] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ message: string; code?: string; status?: number } | null>(null);

  useEffect(() => {
    let active = true;

    async function loadProjects() {
      try {
        const items = await getProjects();
        if (active) {
          setProjects(items.filter((project) => project.status !== "archived"));
          setProjectError("");
        }
      } catch (err) {
        if (active) {
          setProjectError(err instanceof Error ? err.message : t.home.error.projectLoad);
        }
      } finally {
        if (active) {
          setProjectsLoading(false);
        }
      }
    }

    loadProjects();
    return () => {
      active = false;
    };
  }, [t.home.error.projectLoad]);

  function selectProject(projectId: string) {
    setSelectedProjectId(projectId);

    const project = projects.find((item) => String(item.id) === projectId);
    if (!project) {
      return;
    }

    setMarketplace(project.marketplace);
    setCategory(project.category);
    setBudget(project.budget_rmb);
    if (project.target_price_min !== null) {
      setPriceMin(project.target_price_min);
    }
    if (project.target_price_max !== null) {
      setPriceMax(project.target_price_max);
    }
  }

  async function runAnalyze() {
    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const projectId = selectedProjectId ? Number(selectedProjectId) : undefined;
      const report = await analyzeKeyword({
        ...(projectId ? { project_id: projectId } : {}),
        ...(productOpportunityId ? { product_opportunity_id: productOpportunityId } : {}),
        keyword,
        marketplace,
        category,
        budget_rmb: budget,
        target_price_min: priceMin,
        target_price_max: priceMax,
        exclude_red_ocean: excludeRedOcean,
        locale
      });
      router.push(`/reports/${report.report_id}`);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError({ message: err.message, code: err.code, status: err.status });
      } else {
        setError({
          message:
            err instanceof TypeError
              ? t.home.error.connect
              : err instanceof Error
                ? err.message
                : t.home.error.analyzeFailed,
          code: "CLIENT_ERROR"
        });
      }
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
            <div className="text-sm font-medium text-accent">{t.home.eyebrow}</div>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
              {t.home.title}
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-ink/70">
              {t.home.subtitle}
            </p>
          </div>

          <form onSubmit={onSubmit} className="border border-line bg-white p-5" aria-busy={loading}>
            <div className="grid gap-4">
              <label className="grid gap-2">
                <span className="text-sm font-medium text-ink">{t.home.fields.project}</span>
                <div className="relative">
                  <FolderOpen
                    className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink/45"
                    size={18}
                    aria-hidden="true"
                  />
                  <select
                    className="w-full border border-line bg-field py-3 pl-10 pr-3 outline-none focus:border-accent"
                    value={selectedProjectId}
                    onChange={(event) => selectProject(event.target.value)}
                  >
                    <option value="">{t.home.fields.createProject}</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.project_name}
                      </option>
                    ))}
                  </select>
                </div>
                {projectsLoading && !projects.length ? (
                  <span className="text-xs text-ink/55">{t.home.fields.loadingProjects}</span>
                ) : null}
                {projectError ? <span className="text-xs text-red-700">{projectError}</span> : null}
              </label>

              <label className="grid gap-2">
                <span className="text-sm font-medium text-ink">{t.home.fields.keyword}</span>
                <input
                  className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                  value={keyword}
                  onChange={(event) => setKeyword(event.target.value)}
                  required
                />
              </label>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">{t.home.fields.marketplace}</span>
                  <select
                    className="border border-line bg-field px-3 py-3 outline-none focus:border-accent"
                    value={marketplace}
                    onChange={(event) => setMarketplace(event.target.value)}
                  >
                    <option value="US">US</option>
                  </select>
                </label>
                <label className="grid gap-2">
                  <span className="text-sm font-medium text-ink">{t.home.fields.category}</span>
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
                <span className="text-sm font-medium text-ink">{t.home.fields.budget}</span>
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
                  <span className="text-sm font-medium text-ink">{t.home.fields.targetPriceMin}</span>
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
                  <span className="text-sm font-medium text-ink">{t.home.fields.targetPriceMax}</span>
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
                {t.home.fields.excludeRedOcean}
              </label>

              {error ? (
                <div className="border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert">
                  <div className="flex gap-3">
                    <AlertTriangle className="mt-0.5 shrink-0 text-red-600" size={18} aria-hidden="true" />
                    <div className="min-w-0">
                      <div className="font-medium">{t.home.error.title}</div>
                      <p className="mt-1 leading-6">{error.message}</p>
                      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-red-700/80">
                        {error.code ? <span>{error.code}</span> : null}
                        {error.status ? <span>HTTP {error.status}</span> : null}
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}

              <button
                className="flex items-center justify-center gap-2 bg-accent px-4 py-3 font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={18} aria-hidden="true" />
                ) : error ? (
                  <RotateCcw size={18} aria-hidden="true" />
                ) : (
                  <Search size={18} aria-hidden="true" />
                )}
                {loading ? t.home.actions.loading : error ? t.home.actions.retry : t.home.actions.analyze}
              </button>
            </div>
          </form>
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-4">
          <Signal label={t.home.signals.demand[0]} text={t.home.signals.demand[1]} />
          <Signal label={t.home.signals.competition[0]} text={t.home.signals.competition[1]} />
          <Signal label={t.home.signals.profit[0]} text={t.home.signals.profit[1]} />
          <Signal label={t.home.signals.opportunity[0]} text={t.home.signals.opportunity[1]} />
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
