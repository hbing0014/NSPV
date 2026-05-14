import Image from "next/image";
import { AlertTriangle, CheckCircle2, ExternalLink } from "lucide-react";
import type { AnalyzeResponse } from "@/lib/api";
import { ScoreGauge } from "@/components/ScoreGauge";
import { getDictionary, Locale, translateRecommendation, translateRisk } from "@/lib/i18n/dictionaries";

type ReportViewProps = {
  report: AnalyzeResponse;
  locale: Locale;
};

export function ReportView({ report, locale }: ReportViewProps) {
  const t = getDictionary(locale);
  const details = report.score_details;
  const createdAt = new Date(report.created_at).toLocaleString(locale);
  const decisionTone = report.risk_level === "High" ? "danger" : report.risk_level === "Medium" ? "warning" : "success";

  return (
    <div className="space-y-6">
      <section className="border border-line bg-white">
        <div className="grid gap-0 lg:grid-cols-[340px_1fr]">
          <div className="border-b border-line p-5 lg:border-b-0 lg:border-r">
            <div className="text-sm text-ink/60">{t.report.nsfsScore}</div>
            <div className="mt-2 text-6xl font-semibold leading-none text-ink">{report.nsfs_score}</div>
            <div className="mt-4 flex flex-wrap gap-2 text-sm">
              <Badge tone="accent">{translateRecommendation(locale, report.recommendation)}</Badge>
              <Badge tone={decisionTone}>{t.report.risk}: {translateRisk(locale, report.risk_level)}</Badge>
            </div>
            <div className="mt-5 grid gap-2 text-sm text-ink/65">
              <div>{t.report.keyword}: {report.keyword}</div>
              <div>{t.report.report} #{report.report_id}</div>
              <div>{t.report.scoring}: {report.scoring_version}</div>
              <div>{createdAt}</div>
            </div>
          </div>

          <div className="p-5">
            <div className="text-sm text-ink/60">{t.report.decisionSummary}</div>
            <p className="mt-3 text-2xl font-semibold leading-9 text-ink">{report.summary}</p>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <Metric label={t.report.avgPrice} value={formatMoney(details.avg_price)} />
              <Metric label={t.report.avgRating} value={formatNumber(details.avg_rating, locale)} />
              <Metric label={t.report.sponsored} value={formatPercent(details.sponsored_density)} />
              <Metric label={t.report.top10Reviews} value={formatNumber(details.avg_reviews_top10, locale)} />
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <ScoreGauge label={t.report.scores.demand} score={report.demand_score} />
        <ScoreGauge label={t.report.scores.competition} score={report.competition_score} />
        <ScoreGauge label={t.report.scores.profit} score={report.profit_score} />
        <ScoreGauge label={t.report.scores.opportunity} score={report.opportunity_score} />
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        <Panel title={t.report.panels.reviewCompetition}>
          <Metric label={t.report.metrics.top10AvgReviews} value={formatNumber(details.avg_reviews_top10, locale)} />
          <Metric label={t.report.metrics.top3AvgReviews} value={formatNumber(details.avg_reviews_top3, locale)} />
          <Metric label={t.report.metrics.top10MinReviews} value={formatNumber(details.min_reviews_top10, locale)} />
          <Metric label={t.report.metrics.brandConcentration} value={formatPercent(details.brand_concentration)} />
        </Panel>
        <Panel title={t.report.panels.redOceanWarnings}>
          <List items={report.warnings} empty={t.report.empty.warnings} tone="warning" />
        </Panel>
        <Panel title={t.report.panels.profitEstimate}>
          <Metric label={t.report.metrics.netMargin} value={formatPercent(details.net_margin)} />
          <Metric label={t.report.metrics.roi} value={formatPercent(details.roi)} />
          <Metric label={t.report.metrics.breakEvenAcos} value={formatPercent(details.break_even_acos)} />
          <Metric label={t.report.metrics.avgMonthlySales} value={formatNumber(details.avg_monthly_sales, locale)} />
        </Panel>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <Panel title={t.report.panels.opportunitySignals}>
          <div className="grid gap-3 sm:grid-cols-2">
            <Metric label={t.report.metrics.painPoints} value={formatNumber(details.pain_points_count, locale)} />
            <Metric label={t.report.metrics.upgradePotential} value={formatNumber(details.upgrade_potential, locale)} />
            <Metric label={t.report.metrics.listingWeakness} value={formatNumber(details.listing_quality_weakness, locale)} />
            <Metric label={t.report.metrics.homogenization} value={formatNumber(details.homogenization_level, locale)} />
          </div>
          <List items={report.opportunities} empty={t.report.empty.opportunities} tone="success" />
        </Panel>
        <Panel title={t.report.panels.actionSuggestions}>
          <List items={report.suggestions} empty={t.report.empty.suggestions} tone="success" />
        </Panel>
      </section>

      <section className="border border-line bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-5">
          <div>
            <h2 className="text-lg font-semibold text-ink">{t.report.products.title}</h2>
            <p className="mt-1 text-sm text-ink/60">{t.report.products.subtitle}</p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <Badge tone="neutral">{report.products.length} {t.report.products.count}</Badge>
            <Badge tone="neutral">{formatPercent(details.sponsored_density)} {t.report.products.sponsored}</Badge>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1080px] border-collapse text-left text-sm">
            <thead className="bg-field text-ink/70">
              <tr>
                <th className="p-3">{t.report.products.columns.rank}</th>
                <th className="p-3">{t.report.products.columns.product}</th>
                <th className="p-3">{t.report.products.columns.brand}</th>
                <th className="p-3">{t.report.products.columns.price}</th>
                <th className="p-3">{t.report.products.columns.rating}</th>
                <th className="p-3">{t.report.products.columns.reviews}</th>
                <th className="p-3">{t.report.products.columns.sales}</th>
                <th className="p-3">{t.report.products.columns.type}</th>
              </tr>
            </thead>
            <tbody>
              {report.products.map((product, index) => (
                <tr key={product.asin} className="border-t border-line">
                  <td className="p-3 text-ink/70">{index + 1}</td>
                  <td className="p-3">
                    <div className="flex items-center gap-3">
                      {shouldShowProductImage(product.image_url) ? (
                        <Image
                          src={product.image_url ?? ""}
                          alt={product.title}
                          width={48}
                          height={48}
                          className="border border-line"
                        />
                      ) : (
                        <ProductImageFallback rank={index + 1} brand={product.brand} />
                      )}
                      {isValidAmazonProductUrl(product.product_url, product.asin) ? (
                        <a
                          className="block max-w-[460px] break-words text-ink hover:text-accent"
                          href={product.product_url ?? "#"}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {product.title}
                          <ExternalLink className="ml-1 inline" size={13} aria-hidden="true" />
                        </a>
                      ) : (
                        <span className="block max-w-[460px] break-words text-ink">{product.title}</span>
                      )}
                    </div>
                  </td>
                  <td className="p-3">{product.brand}</td>
                  <td className="p-3">${product.price}</td>
                  <td className="p-3">{product.rating}</td>
                  <td className="p-3">{product.review_count}</td>
                  <td className="p-3">{product.monthly_sales_est}</td>
                  <td className="p-3">
                    <span className={product.is_sponsored ? "text-amber" : "text-ink/70"}>
                      {product.is_sponsored ? t.report.products.sponsored : t.report.products.organic}
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

function ProductImageFallback({ rank, brand }: { rank: number; brand: string | null }) {
  const label = brand?.slice(0, 2).toUpperCase() || `#${rank}`;

  return (
    <div
      className="flex h-12 w-12 shrink-0 items-center justify-center border border-line bg-field text-xs font-semibold text-ink/55"
      aria-hidden="true"
    >
      {label}
    </div>
  );
}

function shouldShowProductImage(imageUrl: string | null | undefined) {
  if (!imageUrl) {
    return false;
  }
  return !imageUrl.includes("placehold.co");
}

function isValidAmazonProductUrl(productUrl: string | null | undefined, asin: string) {
  if (!productUrl || !/^B[A-Z0-9]{9}$/.test(asin)) {
    return false;
  }

  try {
    const url = new URL(productUrl);
    return url.hostname.endsWith("amazon.com") && url.pathname.includes(`/dp/${asin}`);
  } catch {
    return false;
  }
}

function formatMoney(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "-";
  }
  return `$${value.toFixed(2)}`;
}

function formatNumber(value: number | null | undefined, locale: Locale = "en") {
  if (value === null || value === undefined) {
    return "-";
  }
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 1 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "-";
  }
  return `${Math.round(value * 100)}%`;
}
