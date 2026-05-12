import Image from "next/image";
import { AlertTriangle, CheckCircle2, ExternalLink } from "lucide-react";
import type { AnalyzeResponse } from "@/lib/api";
import { ScoreGauge } from "@/components/ScoreGauge";

type ReportViewProps = {
  report: AnalyzeResponse;
};

export function ReportView({ report }: ReportViewProps) {
  const details = report.score_details;

  return (
    <div className="space-y-6">
      <section className="grid gap-5 lg:grid-cols-[320px_1fr]">
        <div className="border border-line bg-white p-5">
          <div className="text-sm text-ink/60">NSFS Score</div>
          <div className="mt-2 text-6xl font-semibold text-ink">{report.nsfs_score}</div>
          <div className="mt-4 flex flex-wrap gap-2 text-sm">
            <span className="bg-accent px-3 py-1 text-white">{report.recommendation}</span>
            <span className="bg-field px-3 py-1 text-ink">Risk: {report.risk_level}</span>
          </div>
        </div>
        <div className="border border-line bg-white p-5">
          <div className="text-sm text-ink/60">Conclusion</div>
          <p className="mt-3 text-xl leading-8 text-ink">{report.summary}</p>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <Metric label="Avg Price" value={`$${details.avg_price}`} />
            <Metric label="Avg Rating" value={details.avg_rating.toString()} />
            <Metric label="Sponsored" value={`${Math.round(details.sponsored_density * 100)}%`} />
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
          <Metric label="Top10 Avg Reviews" value={details.avg_reviews_top10.toString()} />
          <Metric label="Top3 Avg Reviews" value={details.avg_reviews_top3.toString()} />
          <Metric label="Top10 Min Reviews" value={details.min_reviews_top10.toString()} />
        </Panel>
        <Panel title="Red Ocean Warnings">
          <List items={report.warnings} empty="No major red ocean warning." tone="warning" />
        </Panel>
        <Panel title="Profit Estimate">
          <Metric label="Net Margin" value={`${Math.round(details.net_margin * 100)}%`} />
          <Metric label="ROI" value={`${Math.round(details.roi * 100)}%`} />
          <Metric label="Break-even ACOS" value={`${Math.round(details.break_even_acos * 100)}%`} />
        </Panel>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <Panel title="Opportunities">
          <List items={report.opportunities} empty="No opportunity signals yet." tone="success" />
        </Panel>
        <Panel title="Action Suggestions">
          <List items={report.suggestions} empty="No suggestions." tone="success" />
        </Panel>
      </section>

      <section className="border border-line bg-white">
        <div className="border-b border-line p-5">
          <h2 className="text-lg font-semibold text-ink">Top20 Products</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[980px] border-collapse text-left text-sm">
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
                        className="max-w-[420px] text-ink hover:text-accent"
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
    <div className="border border-line bg-field p-3">
      <div className="text-xs uppercase text-ink/50">{label}</div>
      <div className="mt-1 text-lg font-semibold text-ink">{value}</div>
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

