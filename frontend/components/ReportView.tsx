import Image from "next/image";
import { AlertTriangle, CheckCircle2, ExternalLink } from "lucide-react";
import type { AnalyzeResponse } from "@/lib/api";
import { ScoreGauge } from "@/components/ScoreGauge";

type ReportViewProps = {
  report: AnalyzeResponse;
};

export function ReportView({ report }: ReportViewProps) {
  const details = report.score_details;
  const createdAt = new Date(report.created_at).toLocaleString();
  const decisionTone = report.risk_level === "High" ? "danger" : report.risk_level === "Medium" ? "warning" : "success";

  return (
    <div className="space-y-6">
      <section className="border border-line bg-white">
        <div className="grid gap-0 lg:grid-cols-[340px_1fr]">
          <div className="border-b border-line p-5 lg:border-b-0 lg:border-r">
            <div className="text-sm text-ink/60">NSFS Score</div>
            <div className="mt-2 text-6xl font-semibold leading-none text-ink">{report.nsfs_score}</div>
            <div className="mt-4 flex flex-wrap gap-2 text-sm">
              <Badge tone="accent">{report.recommendation}</Badge>
              <Badge tone={decisionTone}>Risk: {report.risk_level}</Badge>
            </div>
            <div className="mt-5 grid gap-2 text-sm text-ink/65">
              <div>Keyword: {report.keyword}</div>
              <div>Report #{report.report_id}</div>
              <div>Scoring: {report.scoring_version}</div>
              <div>{createdAt}</div>
            </div>
          </div>

          <div className="p-5">
            <div className="text-sm text-ink/60">Decision Summary</div>
            <p className="mt-3 text-2xl font-semibold leading-9 text-ink">{report.summary}</p>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <Metric label="Avg Price" value={formatMoney(details.avg_price)} />
              <Metric label="Avg Rating" value={formatNumber(details.avg_rating)} />
              <Metric label="Sponsored" value={formatPercent(details.sponsored_density)} />
              <Metric label="Top10 Reviews" value={formatNumber(details.avg_reviews_top10)} />
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <ScoreGauge label="Demand Score" score={report.demand_score} />
        <ScoreGauge label="Competition Score" score={report.competition_score} />
        <ScoreGauge label="Profit Score" score={report.profit_score} />
        <ScoreGauge label="Opportunity Score" score={report.opportunity_score} />
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        <Panel title="Review Competition">
          <Metric label="Top10 Avg Reviews" value={formatNumber(details.avg_reviews_top10)} />
          <Metric label="Top3 Avg Reviews" value={formatNumber(details.avg_reviews_top3)} />
          <Metric label="Top10 Min Reviews" value={formatNumber(details.min_reviews_top10)} />
          <Metric label="Brand Concentration" value={formatPercent(details.brand_concentration)} />
        </Panel>
        <Panel title="Red Ocean Warnings">
          <List items={report.warnings} empty="No major red ocean warning." tone="warning" />
        </Panel>
        <Panel title="Profit Estimate">
          <Metric label="Net Margin" value={formatPercent(details.net_margin)} />
          <Metric label="ROI" value={formatPercent(details.roi)} />
          <Metric label="Break-even ACOS" value={formatPercent(details.break_even_acos)} />
          <Metric label="Avg Monthly Sales" value={formatNumber(details.avg_monthly_sales)} />
        </Panel>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <Panel title="Opportunity Signals">
          <div className="grid gap-3 sm:grid-cols-2">
            <Metric label="Pain Points" value={formatNumber(details.pain_points_count)} />
            <Metric label="Upgrade Potential" value={formatNumber(details.upgrade_potential)} />
            <Metric label="Listing Weakness" value={formatNumber(details.listing_quality_weakness)} />
            <Metric label="Homogenization" value={formatNumber(details.homogenization_level)} />
          </div>
          <List items={report.opportunities} empty="No opportunity signals yet." tone="success" />
        </Panel>
        <Panel title="Action Suggestions">
          <List items={report.suggestions} empty="No suggestions." tone="success" />
        </Panel>
      </section>

      <section className="border border-line bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-5">
          <div>
            <h2 className="text-lg font-semibold text-ink">Top20 Products</h2>
            <p className="mt-1 text-sm text-ink/60">Snapshot used for this report.</p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <Badge tone="neutral">{report.products.length} products</Badge>
            <Badge tone="neutral">{formatPercent(details.sponsored_density)} sponsored</Badge>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1080px] border-collapse text-left text-sm">
            <thead className="bg-field text-ink/70">
              <tr>
                <th className="p-3">Rank</th>
                <th className="p-3">Product</th>
                <th className="p-3">Brand</th>
                <th className="p-3">Price</th>
                <th className="p-3">Rating</th>
                <th className="p-3">Reviews</th>
                <th className="p-3">Sales Est.</th>
                <th className="p-3">Type</th>
              </tr>
            </thead>
            <tbody>
              {report.products.map((product, index) => (
                <tr key={product.asin} className="border-t border-line">
                  <td className="p-3 text-ink/70">{index + 1}</td>
                  <td className="p-3">
                    <div className="flex items-center gap-3">
                      {product.image_url ? (
                        <Image
                          src={product.image_url}
                          alt=""
                          width={48}
                          height={48}
                          className="border border-line"
                        />
                      ) : null}
                      <a
                        className="block max-w-[460px] break-words text-ink hover:text-accent"
                        href={product.product_url ?? "#"}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {product.title}
                        <ExternalLink className="ml-1 inline" size={13} aria-hidden="true" />
                      </a>
                    </div>
                  </td>
                  <td className="p-3">{product.brand}</td>
                  <td className="p-3">${product.price}</td>
                  <td className="p-3">{product.rating}</td>
                  <td className="p-3">{product.review_count}</td>
                  <td className="p-3">{product.monthly_sales_est}</td>
                  <td className="p-3">
                    <span className={product.is_sponsored ? "text-amber" : "text-ink/70"}>
                      {product.is_sponsored ? "Sponsored" : "Organic"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 border border-line bg-field p-3">
      <div className="text-xs uppercase text-ink/50">{label}</div>
      <div className="mt-1 break-words text-lg font-semibold text-ink">{value}</div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border border-line bg-white p-5">
      <h2 className="text-lg font-semibold text-ink">{title}</h2>
      <div className="mt-4 space-y-3">{children}</div>
    </div>
  );
}

function List({
  items,
  empty,
  tone
}: {
  items: string[];
  empty: string;
  tone: "warning" | "success";
}) {
  if (!items.length) {
    return <p className="text-sm text-ink/60">{empty}</p>;
  }

  const Icon = tone === "warning" ? AlertTriangle : CheckCircle2;

  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item} className="flex gap-3 text-sm text-ink">
          <Icon
            className={tone === "warning" ? "mt-0.5 text-amber" : "mt-0.5 text-accent"}
            size={16}
            aria-hidden="true"
          />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function Badge({
  tone,
  children
}: {
  tone: "accent" | "success" | "warning" | "danger" | "neutral";
  children: React.ReactNode;
}) {
  const className = {
    accent: "bg-accent text-white",
    success: "bg-emerald-50 text-emerald-800",
    warning: "bg-amber/15 text-ink",
    danger: "bg-red-50 text-red-800",
    neutral: "bg-field text-ink"
  }[tone];

  return <span className={`px-3 py-1 ${className}`}>{children}</span>;
}

function formatMoney(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "-";
  }
  return `$${value.toFixed(2)}`;
}

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "-";
  }
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "-";
  }
  return `${Math.round(value * 100)}%`;
}
