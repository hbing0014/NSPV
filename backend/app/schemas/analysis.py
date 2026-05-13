from datetime import datetime

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    project_id: int | None = Field(default=None, gt=0)
    keyword: str = Field(min_length=2, max_length=255)
    marketplace: str = "US"
    category: str = "Kitchen & Dining"
    budget_rmb: float = Field(gt=0)
    target_price_min: float = Field(gt=0)
    target_price_max: float = Field(gt=0)
    exclude_red_ocean: bool = True


class ProductOut(BaseModel):
    asin: str
    title: str
    brand: str | None = None
    price: float | None = None
    rating: float | None = None
    review_count: int | None = None
    monthly_sales_est: int | None = None
    monthly_revenue_est: float | None = None
    bsr: int | None = None
    is_sponsored: bool = False
    seller_type: str | None = None
    image_url: str | None = None
    product_url: str | None = None
    organic_rank: int | None = None
    sponsored_rank: int | None = None


class ScoreDetails(BaseModel):
    monthly_search_volume: int
    avg_monthly_sales: float
    search_trend: str
    seasonality_score: float
    avg_price: float
    avg_rating: float
    avg_reviews_top10: float
    avg_reviews_top3: float
    min_reviews_top10: int
    sponsored_density: float
    brand_concentration: float
    amazon_basics_present: bool
    net_margin: float
    roi: float
    break_even_acos: float
    negative_review_density: float
    pain_points_count: int
    listing_quality_weakness: float
    homogenization_level: float
    upgrade_potential: float


class AnalyzeResponse(BaseModel):
    report_id: int
    project_id: int
    keyword_id: int
    keyword: str
    nsfs_score: float
    recommendation: str
    risk_level: str
    demand_score: float
    competition_score: float
    profit_score: float
    opportunity_score: float
    summary: str
    warnings: list[str]
    suggestions: list[str]
    opportunities: list[str]
    score_details: ScoreDetails
    products: list[ProductOut]
    created_at: datetime


class ReportListItem(BaseModel):
    report_id: int
    project_id: int
    keyword: str
    nsfs_score: float
    recommendation: str
    risk_level: str
    created_at: datetime
