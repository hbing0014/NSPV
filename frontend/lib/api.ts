export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export type Product = {
  asin: string;
  title: string;
  brand: string | null;
  price: number | null;
  rating: number | null;
  review_count: number | null;
  monthly_sales_est: number | null;
  monthly_revenue_est: number | null;
  bsr: number | null;
  is_sponsored: boolean;
  seller_type: string | null;
  image_url: string | null;
  product_url: string | null;
  organic_rank: number | null;
  sponsored_rank: number | null;
};

export type ScoreDetails = {
  monthly_search_volume: number;
  avg_monthly_sales: number;
  search_trend: string;
  seasonality_score: number;
  avg_price: number;
  avg_rating: number;
  avg_reviews_top10: number;
  avg_reviews_top3: number;
  min_reviews_top10: number;
  sponsored_density: number;
  brand_concentration: number;
  amazon_basics_present: boolean;
  net_margin: number;
  roi: number;
  break_even_acos: number;
  negative_review_density: number;
  pain_points_count: number;
  listing_quality_weakness: number;
  homogenization_level: number;
  upgrade_potential: number;
};

export type AnalyzeResponse = {
  report_id: number;
  project_id: number;
  keyword_id: number;
  keyword: string;
  nsfs_score: number;
  recommendation: string;
  risk_level: string;
  demand_score: number;
  competition_score: number;
  profit_score: number;
  opportunity_score: number;
  summary: string;
  warnings: string[];
  suggestions: string[];
  opportunities: string[];
  score_details: ScoreDetails;
  products: Product[];
  created_at: string;
};

export type ReportListItem = {
  report_id: number;
  project_id: number;
  keyword: string;
  nsfs_score: number;
  recommendation: string;
  risk_level: string;
  created_at: string;
};

export async function analyzeKeyword(payload: {
  keyword: string;
  marketplace: string;
  category: string;
  budget_rmb: number;
  target_price_min: number;
  target_price_max: number;
  exclude_red_ocean: boolean;
}) {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail ?? "Analyze request failed");
  }

  return (await response.json()) as AnalyzeResponse;
}

export async function getReport(reportId: string) {
  const response = await fetch(`${API_BASE}/api/reports/${reportId}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("Report not found");
  }

  return (await response.json()) as AnalyzeResponse;
}

export async function getReports() {
  const response = await fetch(`${API_BASE}/api/reports`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("Failed to load reports");
  }

  return (await response.json()) as ReportListItem[];
}

