"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, FolderOpen, Loader2, RotateCcw, Search } from "lucide-react";
import { Header } from "@/components/Header";
import { ApiRequestError, Project, analyzeKeyword, getProjects } from "@/lib/api";

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
          setProjectError(err instanceof Error ? err.message : "Failed to load projects");
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
  }, []);

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
      if (err instanceof ApiRequestError) {
        setError({ message: err.message, code: err.code, status: err.status });
      } else {
        setError({
          message:
            err instanceof TypeError
              ? "Cannot connect to NSPV API. Check the backend server and try again."
              : err instanceof Error
                ? err.message
                : "Analyze failed. Please try again.",
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
            <div className="text-sm font-medium text-accent">New Seller Product Validator</div>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
              Amazon 新店选品风险判断
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-ink/70">
              输入一个美国站关键词，系统会分析首页 Top20 商品结构，生成 NSFS 评分、红海预警和进入建议。
            </p>
          </div>

          <form onSubmit={onSubmit} className="border border-line bg-white p-5" aria-busy={loading}>
            <div className="grid gap-4">
              <label className="grid gap-2">
                <span className="text-sm font-medium text-ink">Project</span>
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
                    disabled={projectsLoading}
                  >
                    <option value="">
                      {projectsLoading ? "Loading projects..." : "Create new project from this analysis"}
                    </option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.project_name}
                      </option>
                    ))}
                  </select>
                </div>
                {projectError ? <span className="text-xs text-red-700">{projectError}</span> : null}
              </label>

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
                <div className="border border-red-200 bg-red-50 p-3 text-sm text-red-800" role="alert">
                  <div className="flex gap-3">
                    <AlertTriangle className="mt-0.5 shrink-0 text-red-600" size={18} aria-hidden="true" />
                    <div className="min-w-0">
                      <div className="font-medium">Analysis failed</div>
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
                {loading ? "Analyzing Amazon Top20..." : error ? "Retry Analyze" : "Analyze"}
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
