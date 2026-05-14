import Link from "next/link";
import { AlertTriangle, ArrowLeft, Search } from "lucide-react";
import { Header } from "@/components/Header";
import { getRadarProduct } from "@/lib/api";
import { getDictionary } from "@/lib/i18n/dictionaries";
import { getServerLocale } from "@/lib/i18n/server";

type ProductDetailPageProps = {
  params: Promise<{ id: string }>;
};

export default async function ProductDetailPage({ params }: ProductDetailPageProps) {
  const { id } = await params;
  const locale = await getServerLocale();
  const t = getDictionary(locale);
  const product = await getRadarProduct(id).catch(() => null);

  if (!product) {
    return (
      <>
        <Header />
        <main className="mx-auto max-w-7xl px-5 py-8">
          <div className="border border-red-200 bg-red-50 p-6 text-red-800">
            <div className="flex items-center gap-3">
              <AlertTriangle size={20} aria-hidden="true" />
              <div className="font-medium">{t.productDetail.notFound}</div>
            </div>
            <Link className="mt-4 inline-flex border border-red-200 bg-white px-3 py-2 text-sm font-medium" href="/radar">
              {t.productDetail.back}
            </Link>
          </div>
        </main>
      </>
    );
  }

  const validateHref = `/validate?${new URLSearchParams({
    keyword: product.primary_keyword,
    category: product.category ?? "",
    budget_rmb: String(Math.round(product.estimated_budget_rmb)),
    target_price_min: String(Math.max(1, Math.floor(product.avg_price * 0.8))),
    target_price_max: String(Math.ceil(product.avg_price * 1.2)),
    product_opportunity_id: String(product.product_opportunity_id)
  }).toString()}`;

  return (
    <>
      <Header />
      <main className="mx-auto max-w-7xl px-5 py-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <Link className="inline-flex items-center gap-2 text-sm font-medium text-ink/70" href="/radar">
            <ArrowLeft size={16} aria-hidden="true" />
            {t.productDetail.back}
          </Link>
          <Link className="inline-flex items-center gap-2 bg-accent px-4 py-3 font-medium text-white" href={validateHref}>
            <Search size={18} aria-hidden="true" />
            {t.productDetail.validate}
          </Link>
        </div>

        <section className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <div className="border border-line bg-white p-5">
            <div className="text-sm font-medium text-accent">{product.category}</div>
            <h1 className="mt-2 text-3xl font-semibold text-ink">{product.product_name}</h1>
            <div className="mt-3 text-sm text-ink/65">
              {t.productDetail.primaryKeyword}: <span className="font-medium text-ink">{product.primary_keyword}</span>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-4">
              <Metric label="NPFS" value={product.npfs_score} />
              <Metric label="Launch" value={product.launch_score} />
              <Metric label="Supplier" value={product.supplier_score} />
              <Metric label={t.productDetail.risk} value={product.risk_level} />
            </div>
          </div>

          <div className="border border-line bg-white p-5">
            <h2 className="font-semibold text-ink">{t.productDetail.launchBudget}</h2>
            <div className="mt-4 grid gap-3 text-sm">
              <Row label={t.productDetail.estimatedBudget} value={`¥${Math.round(product.estimated_budget_rmb).toLocaleString()}`} />
              <Row label="MOQ" value={product.estimated_moq} />
              <Row label={t.productDetail.launchDays} value={product.estimated_launch_days} />
              <Row label={t.productDetail.avgPrice} value={`$${product.avg_price.toFixed(2)}`} />
            </div>
          </div>
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <Panel title={t.productDetail.competition}>
            <Row label="Top10 Avg Reviews" value={product.avg_reviews_top10} />
            <Row label="Top10 Min Reviews" value={product.min_reviews_top10} />
            <Row label="Avg Rating" value={product.avg_rating} />
          </Panel>
          <Panel title={t.productDetail.profit}>
            <Row label="Profit Score" value={product.profit_score} />
            <Row label="Demand Score" value={product.demand_score} />
            <Row label="Opportunity Score" value={product.opportunity_score} />
          </Panel>
          <Panel title={t.productDetail.risks}>
            <Flag label="Red Ocean" active={product.is_red_ocean} />
            <Flag label="Amazon Basics" active={product.is_amazon_basics} />
            <Flag label="Fragile" active={product.is_fragile} />
            <Flag label="Seasonal" active={product.is_seasonal} />
            <Flag label="Heavy" active={product.is_heavy} />
            <Flag label="Patent Risk" active={product.is_patent_risk} />
          </Panel>
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          <ListPanel title={t.productDetail.differentiation} items={product.differentiation_paths} empty={t.productDetail.empty} />
          <ListPanel title={t.productDetail.keyRisks} items={product.key_risks} empty={t.productDetail.empty} />
        </section>
      </main>
    </>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="border border-line bg-field p-3">
      <div className="text-xs text-ink/55">{label}</div>
      <div className="mt-1 text-xl font-semibold text-ink">{value}</div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border border-line bg-white p-5">
      <h2 className="font-semibold text-ink">{title}</h2>
      <div className="mt-4 grid gap-3 text-sm">{children}</div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-ink/60">{label}</span>
      <span className="font-medium text-ink">{value}</span>
    </div>
  );
}

function Flag({ label, active }: { label: string; active: boolean }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-ink/60">{label}</span>
      <span className={active ? "font-medium text-red-700" : "font-medium text-emerald-700"}>{active ? "Yes" : "No"}</span>
    </div>
  );
}

function ListPanel({ title, items, empty }: { title: string; items: string[]; empty: string }) {
  return (
    <div className="border border-line bg-white p-5">
      <h2 className="font-semibold text-ink">{title}</h2>
      {items.length ? (
        <ul className="mt-4 grid gap-2 text-sm text-ink/70">
          {items.map((item) => (
            <li key={item} className="border border-line bg-field px-3 py-2">
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <div className="mt-4 text-sm text-ink/55">{empty}</div>
      )}
    </div>
  );
}
