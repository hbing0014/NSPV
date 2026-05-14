from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


RiskPreference = Literal["low", "balanced", "aggressive"]
RiskLevel = Literal["low", "medium", "high"]
Recommendation = Literal["strongly_recommended", "worth_research", "caution", "avoid"]
ScanType = Literal["full_scan", "incremental_scan"]
SourceType = Literal["best_sellers", "new_releases", "search_pool", "bsr_scan"]
ScanStatus = Literal["pending", "running", "completed", "failed"]
PriorityLevel = Literal["high", "medium", "low"]
RadarSort = Literal["highest_npfs", "lowest_risk", "lowest_budget", "highest_profit", "easiest_launch"]


class DiscoveryRequest(BaseModel):
    project_id: int | None = Field(default=None, gt=0)
    category: str = Field(min_length=1, max_length=100)
    marketplace: str = Field(default="US", max_length=20)
    budget_rmb: float = Field(gt=0)
    risk_preference: RiskPreference = "balanced"
    price_min: float | None = Field(default=None, gt=0)
    price_max: float | None = Field(default=None, gt=0)
    weight_limit: float | None = Field(default=None, gt=0)
    weight_limit_g: float | None = Field(default=None, gt=0)
    exclude_red_ocean: bool = True
    exclude_amazon_basics: bool = True
    exclude_fragile: bool = True
    exclude_seasonal: bool = True
    low_moq_only: bool = False
    easy_launch_only: bool = False
    high_margin_only: bool = False
    min_launch_score: float | None = Field(default=None, ge=0, le=100)
    min_npfs: float | None = Field(default=None, ge=0, le=100)
    max_review_barrier: int | None = Field(default=None, ge=0)
    locale: Literal["zh-CN", "en"] = "zh-CN"

    @model_validator(mode="after")
    def validate_price_range(self) -> "DiscoveryRequest":
        if self.price_min is not None and self.price_max is not None and self.price_min > self.price_max:
            raise ValueError("price_min cannot exceed price_max")
        return self

    @property
    def weight_limit_kg(self) -> float | None:
        if self.weight_limit is not None:
            return self.weight_limit
        if self.weight_limit_g is not None:
            return self.weight_limit_g / 1000
        return None


class CategoryOut(BaseModel):
    id: int
    category_name: str
    parent_category: str | None = None
    amazon_category_id: str | None = None
    marketplace: str
    is_active: bool
    priority_level: PriorityLevel | str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategoryScanJobOut(BaseModel):
    id: int
    category_id: int
    marketplace: str
    scan_type: ScanType | str
    source_type: SourceType | str
    status: ScanStatus | str
    total_products_found: int
    total_products_filtered: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryProductOut(BaseModel):
    id: int
    scan_job_id: int
    category_id: int
    asin: str
    title: str
    brand: str | None = None
    price: float | None = None
    rating: float | None = None
    review_count: int | None = None
    bsr: int | None = None
    is_sponsored: bool = False
    seller_type: str | None = None
    weight: float | None = None
    dimensions: dict = Field(default_factory=dict)
    is_fragile: bool = False
    estimated_monthly_sales: int | None = None
    estimated_monthly_revenue: float | None = None
    amazon_basics_present: bool = False
    seasonality_score: float | None = None
    patent_risk_level: str = "unknown"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LaunchScoreOut(BaseModel):
    id: int
    product_opportunity_id: int | None = None
    asin: str
    estimated_moq: int | None = None
    estimated_unit_cost_rmb: float | None = None
    estimated_shipping_cost_rmb: float | None = None
    estimated_packaging_complexity: str | None = None
    estimated_ppc_launch_cost: float | None = None
    estimated_review_difficulty: float | None = None
    estimated_inventory_cycle_days: int | None = None
    estimated_total_launch_budget: float | None = None
    launch_score: float = Field(ge=0, le=100)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductOpportunityOut(BaseModel):
    id: int
    category_id: int | None = None
    asin: str
    product_name: str
    brand: str | None = None
    primary_keyword: str
    keyword_cluster_id: int | None = None
    avg_price: float
    avg_rating: float
    avg_reviews_top10: float
    min_reviews_top10: int
    monthly_search_volume: int
    estimated_monthly_sales: int
    estimated_monthly_revenue: float
    demand_score: float = Field(ge=0, le=100)
    competition_score: float = Field(ge=0, le=100)
    profit_score: float = Field(ge=0, le=100)
    opportunity_score: float = Field(ge=0, le=100)
    launch_score: float = Field(ge=0, le=100)
    supplier_score: float = Field(ge=0, le=100)
    npfs_score: float = Field(ge=0, le=100)
    estimated_budget_rmb: float
    estimated_moq: int
    estimated_first_order_qty: int
    estimated_launch_days: int
    risk_level: RiskLevel | str
    recommendation: Recommendation | str
    is_red_ocean: bool
    is_amazon_basics: bool
    is_fragile: bool
    is_seasonal: bool
    is_heavy: bool
    is_patent_risk: bool
    differentiation_paths: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    key_opportunities: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DiscoveryReportOut(BaseModel):
    id: int
    project_id: int
    user_id: int | None = None
    input_category: str
    input_budget_rmb: float
    input_risk_preference: str
    input_price_min: float | None = None
    input_price_max: float | None = None
    input_weight_limit: float | None = None
    exclude_red_ocean: bool
    exclude_amazon_basics: bool
    total_products_scanned: int
    total_products_filtered: int
    total_recommendations: int
    recommended_products: list[int] = Field(default_factory=list)
    summary: str
    strategy_advice: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DiscoverProductOut(BaseModel):
    product_opportunity_id: int
    asin: str
    product_name: str
    category: str
    primary_keyword: str
    secondary_keywords: list[str] = Field(default_factory=list)
    long_tail_keywords: list[str] = Field(default_factory=list)
    avg_price: float
    avg_rating: float
    avg_reviews_top10: float
    min_reviews_top10: int
    sponsored_density: float
    npfs_score: float
    demand_score: float
    competition_score: float
    profit_score: float
    opportunity_score: float
    launch_score: float
    supplier_score: float
    estimated_budget_rmb: float
    estimated_moq: int
    estimated_launch_days: int
    risk_level: str
    recommendation: str
    tags: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    key_opportunities: list[str] = Field(default_factory=list)


class DiscoverProductsResponse(BaseModel):
    discovery_report_id: int
    project_id: int
    total_products_scanned: int
    total_products_filtered: int
    total_recommendations: int
    products: list[DiscoverProductOut]


class RadarProductOut(BaseModel):
    product_opportunity_id: int
    asin: str
    product_name: str
    category: str | None = None
    primary_keyword: str
    avg_price: float
    avg_rating: float
    avg_reviews_top10: float
    min_reviews_top10: int
    npfs_score: float
    demand_score: float
    competition_score: float
    profit_score: float
    opportunity_score: float
    launch_score: float
    supplier_score: float
    estimated_budget_rmb: float
    estimated_moq: int
    estimated_launch_days: int
    risk_level: str
    recommendation: str
    is_red_ocean: bool
    is_amazon_basics: bool
    is_fragile: bool
    is_seasonal: bool
    is_heavy: bool
    is_patent_risk: bool
    differentiation_paths: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    key_opportunities: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class RadarProductsResponse(BaseModel):
    total: int
    products: list[RadarProductOut]
