import Link from "next/link";
import { Bookmark, Eye, Search } from "lucide-react";
import { DiscoverProduct } from "@/lib/api";

type ProductOpportunityCardProps = {
  product: DiscoverProduct;
  labels: {
    npfs: string;
    launch: string;
    risk: string;
    budget: string;
    avgPrice: string;
    primaryKeyword: string;
    viewDetail: string;
    validate: string;
    save: string;
  };
};

export function ProductOpportunityCard({ product, labels }: ProductOpportunityCardProps) {
  const tags = product.tags.slice(0, 4);

  return (
    <article className="grid gap-4 border border-line bg-white p-4 sm:grid-cols-[104px_1fr]">
      <div className="flex aspect-square items-center justify-center border border-line bg-field text-center text-xs font-medium uppercase tracking-wide text-ink/50">
        NSPV
      </div>
      <div className="min-w-0">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="text-xs font-medium uppercase tracking-wide text-accent">{product.category}</div>
            <h3 className="mt-1 text-lg font-semibold leading-snug text-ink">{product.product_name}</h3>
            <div className="mt-1 text-sm text-ink/65">
              {labels.primaryKeyword}: <span className="font-medium text-ink">{product.primary_keyword}</span>
            </div>
          </div>
          <Score label={labels.npfs} value={product.npfs_score} />
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-4">
          <Metric label={labels.avgPrice} value={`$${product.avg_price.toFixed(2)}`} />
          <Metric label={labels.launch} value={String(product.launch_score)} />
          <Metric label={labels.risk} value={product.risk_level} />
          <Metric label={labels.budget} value={`¥${Math.round(product.estimated_budget_rmb).toLocaleString()}`} />
        </div>

        {tags.length ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {tags.map((tag) => (
              <span key={tag} className="bg-field px-2 py-1 text-xs font-medium text-ink/70">
                {tag}
              </span>
            ))}
          </div>
        ) : null}

        <div className="mt-4 flex flex-wrap gap-2">
          <Link
            className="inline-flex items-center gap-2 border border-line px-3 py-2 text-sm font-medium text-ink"
            href={`/radar/products/${product.product_opportunity_id}`}
          >
            <Eye size={16} aria-hidden="true" />
            {labels.viewDetail}
          </Link>
          <Link
            className="inline-flex items-center gap-2 bg-accent px-3 py-2 text-sm font-medium text-white"
            href={`/validate?keyword=${encodeURIComponent(product.primary_keyword)}`}
          >
            <Search size={16} aria-hidden="true" />
            {labels.validate}
          </Link>
          <button className="inline-flex items-center gap-2 border border-line px-3 py-2 text-sm font-medium text-ink" type="button">
            <Bookmark size={16} aria-hidden="true" />
            {labels.save}
          </button>
        </div>
      </div>
    </article>
  );
}

function Score({ label, value }: { label: string; value: number }) {
  return (
    <div className="min-w-20 border border-line bg-field px-3 py-2 text-right">
      <div className="text-xs text-ink/60">{label}</div>
      <div className="text-2xl font-semibold text-ink">{value}</div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-ink/55">{label}</div>
      <div className="mt-1 text-sm font-medium text-ink">{value}</div>
    </div>
  );
}
