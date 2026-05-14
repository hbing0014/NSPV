export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

type ApiErrorBody = {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
  detail?: string;
};

export class ApiRequestError extends Error {
  status: number;
  code: string;
  details: unknown;

  constructor(message: string, status: number, code = "REQUEST_FAILED", details: unknown = null) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

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
  scraper_run_id: number | null;
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
  input_payload: Record<string, unknown>;
  scoring_version: string;
  analysis_status: string;
  error_message: string | null;
  created_at: string;
};

export type Project = {
  id: number;
  project_name: string;
  category: string;
  budget_rmb: number;
  marketplace: string;
  target_price_min: number | null;
  target_price_max: number | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type ReportListItem = {
  report_id: number;
  project_id: number;
  scraper_run_id: number | null;
  keyword: string;
  nsfs_score: number;
  recommendation: string;
  risk_level: string;
  analysis_status: string;
  created_at: string;
};

export async function analyzeKeyword(payload: {
  project_id?: number;
  keyword: string;
  marketplace: string;
  category: string;
  budget_rmb: number;
  target_price_min: number;
  target_price_max: number;
  exclude_red_ocean: boolean;
  locale?: "zh-CN" | "en";
}) {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw await toApiRequestError(response, "Analyze request failed");
  }

  return (await response.json()) as AnalyzeResponse;
}

export async function getProjects() {
  const response = await fetch(`${API_BASE}/api/projects`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw await toApiRequestError(response, "Failed to load projects");
  }

  return (await response.json()) as Project[];
}

export async function getReport(reportId: string) {
  const response = await fetch(`${API_BASE}/api/reports/${reportId}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw await toApiRequestError(response, "Report not found");
  }

  return (await response.json()) as AnalyzeResponse;
}

export async function getReports() {
  const response = await fetch(`${API_BASE}/api/reports`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw await toApiRequestError(response, "Failed to load reports");
  }

  return (await response.json()) as ReportListItem[];
}

async function toApiRequestError(response: Response, fallbackMessage: string) {
  const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
  const message = body.error?.message ?? body.detail ?? fallbackMessage;
  const code = body.error?.code ?? "REQUEST_FAILED";
  return new ApiRequestError(message, response.status, code, body.error?.details ?? null);
}
