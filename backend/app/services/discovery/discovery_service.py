from dataclasses import dataclass, field

from app.schemas.discovery import DiscoveryRequest
from app.services.discovery.category_scanner import ScannedProduct, scan_products
from app.services.discovery.keyword_clusters import KeywordCluster, generate_keyword_cluster
from app.services.discovery.launch_score import LaunchScoreInput, calculate_launch_score
from app.services.discovery.npfs import NPFSInput, calculate_npfs
from app.services.discovery.rules import ProductLayer, ProductTag, ScannerRuleConfig
from app.services.discovery.seed_products import SeedProduct
from app.services.discovery.supplier_score import SupplierScoreInput, calculate_supplier_score


USD_TO_RMB = 7.2


@dataclass(frozen=True)
class DiscoveredProduct:
    source: SeedProduct
    scanned: ScannedProduct
    keyword_cluster: KeywordCluster
    demand_score: float
    competition_score: float
    profit_score: float
    opportunity_score: float
    launch_score: float
    supplier_score: float
    npfs_score: float
    estimated_budget_rmb: float
    estimated_moq: int
    estimated_launch_days: int
    risk_level: str
    recommendation: str
    tags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    key_opportunities: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DiscoverProductsResult:
    total_products_scanned: int
    total_products_filtered: int
    products: list[DiscoveredProduct]

    @property
    def total_recommendations(self) -> int:
        return len(self.products)


def discover_products(request: DiscoveryRequest) -> DiscoverProductsResult:
    config = ScannerRuleConfig(
        min_price=request.price_min or 15,
        max_price=request.price_max or 80,
        max_weight_kg=request.weight_limit_kg or 1,
        exclude_red_ocean=request.exclude_red_ocean,
        exclude_amazon_basics=request.exclude_amazon_basics,
        exclude_fragile=request.exclude_fragile,
        exclude_seasonal=request.exclude_seasonal,
    )
    scan_result = scan_products(config=config, category=request.category)

    discovered: list[DiscoveredProduct] = []
    for scanned in scan_result.products:
        if scanned.layer == ProductLayer.REJECTED:
            continue
        product = scanned.product
        demand = estimate_demand_score(product)
        competition = estimate_competition_score(product)
        profit = estimate_profit_score(product)
        opportunity = estimate_opportunity_score(scanned)
        launch = calculate_launch_score(build_launch_input(product, request.budget_rmb))
        supplier = calculate_supplier_score(build_supplier_input(product))
        npfs = calculate_npfs(
            NPFSInput(
                demand_score=demand,
                competition_score=competition,
                profit_score=profit,
                opportunity_score=opportunity,
                launch_score=launch.launch_score,
                supplier_score=supplier.supplier_score,
                warnings=list(scanned.evaluation.warnings),
                is_red_ocean=ProductTag.RED_OCEAN in scanned.tags,
                is_amazon_basics=product.amazon_basics_present,
                is_fragile=product.is_fragile,
                is_heavy=product.weight_kg is not None and product.weight_kg > 1,
                is_patent_risk=product.patent_risk_level == "high",
            )
        )

        if request.risk_preference == "low" and npfs.risk_level.value == "high":
            continue
        if request.min_launch_score is not None and launch.launch_score < request.min_launch_score:
            continue
        if request.min_npfs is not None and npfs.npfs_score < request.min_npfs:
            continue
        if request.max_review_barrier is not None and product.min_reviews_top10 > request.max_review_barrier:
            continue
        if request.low_moq_only and supplier.moq_score < 85:
            continue
        if request.easy_launch_only and launch.launch_score < 80:
            continue
        if request.high_margin_only and profit < 80:
            continue

        discovered.append(
            DiscoveredProduct(
                source=product,
                scanned=scanned,
                keyword_cluster=generate_keyword_cluster(product),
                demand_score=demand,
                competition_score=competition,
                profit_score=profit,
                opportunity_score=opportunity,
                launch_score=launch.launch_score,
                supplier_score=supplier.supplier_score,
                npfs_score=npfs.npfs_score,
                estimated_budget_rmb=launch.estimated_total_launch_budget,
                estimated_moq=build_supplier_input(product).avg_supplier_moq,
                estimated_launch_days=launch.estimated_launch_days,
                risk_level=npfs.risk_level.value,
                recommendation=npfs.recommendation.value,
                tags=sorted({tag.value for tag in scanned.tags} | {tag.value for tag in launch.tags} | {tag.value for tag in supplier.tags}),
                warnings=npfs.warnings,
                key_opportunities=build_key_opportunities(scanned),
            )
        )

    return DiscoverProductsResult(
        total_products_scanned=scan_result.total_products_scanned,
        total_products_filtered=scan_result.total_products_filtered,
        products=sorted(discovered, key=lambda item: item.npfs_score, reverse=True),
    )


def estimate_demand_score(product: SeedProduct) -> float:
    if product.estimated_monthly_sales >= 1500:
        return 95
    if product.estimated_monthly_sales >= 900:
        return 85
    if product.estimated_monthly_sales >= 600:
        return 75
    if product.estimated_monthly_sales >= 400:
        return 60
    return 40


def estimate_competition_score(product: SeedProduct) -> float:
    if product.avg_reviews_top10 < 300:
        review_score = 90
    elif product.avg_reviews_top10 < 800:
        review_score = 75
    elif product.avg_reviews_top10 < 1500:
        review_score = 55
    else:
        review_score = 25

    if product.sponsored_density < 0.30:
        sponsored_score = 85
    elif product.sponsored_density < 0.50:
        sponsored_score = 60
    else:
        sponsored_score = 35
    return round(review_score * 0.70 + sponsored_score * 0.30, 2)


def estimate_profit_score(product: SeedProduct) -> float:
    if 20 <= product.avg_price <= 40:
        return 85
    if 15 <= product.avg_price < 20 or 40 < product.avg_price <= 50:
        return 70
    if 50 < product.avg_price <= 80:
        return 55
    return 35


def estimate_opportunity_score(scanned: ScannedProduct) -> float:
    score = 65
    if ProductTag.STRONG_OPPORTUNITY in scanned.tags:
        score += 25
    if ProductTag.LOW_REVIEW in scanned.tags:
        score += 10
    if ProductTag.HIGH_PPC in scanned.tags:
        score -= 15
    if ProductTag.MATURE_MARKET in scanned.tags:
        score -= 10
    return max(0, min(100, score))


def build_launch_input(product: SeedProduct, user_budget_rmb: float) -> LaunchScoreInput:
    unit_cost = max(product.avg_price * USD_TO_RMB * 0.25, 8)
    first_order_qty = estimated_moq(product)
    return LaunchScoreInput(
        product_name=product.product_name,
        user_budget_rmb=user_budget_rmb,
        estimated_unit_cost_rmb=round(unit_cost, 2),
        estimated_first_order_qty=first_order_qty,
        estimated_shipping_cost_rmb=round(first_order_qty * max(product.weight_kg or 0.3, 0.1) * 18, 2),
        estimated_packaging_cost_rmb=round(first_order_qty * packaging_cost_per_unit(product), 2),
        estimated_ppc_seed_budget_rmb=round(product.avg_price * USD_TO_RMB * 35, 2),
        avg_cpc_usd=estimated_cpc(product),
        sponsored_density=product.sponsored_density,
        min_reviews_top10=product.min_reviews_top10,
        avg_supplier_moq=first_order_qty,
        customization_level="simple_label" if product.patent_risk_level == "low" else "light_custom",
        estimated_monthly_sales=product.estimated_monthly_sales,
        weight_kg=product.weight_kg,
        is_fragile=product.is_fragile,
        variation_count=1,
        high_return_risk=product.is_fragile,
        complex_installation=False,
    )


def build_supplier_input(product: SeedProduct) -> SupplierScoreInput:
    moq = estimated_moq(product)
    complexity = "high" if product.patent_risk_level == "high" else "medium" if product.patent_risk_level == "medium" else "low"
    packaging_complexity = "high" if product.is_fragile else "medium" if (product.weight_kg or 0) > 0.7 else "low"
    supplier_count = 90 if product.sample_type in {"low_risk", "low_review"} else 45 if complexity == "medium" else 25
    unit_cost = max(product.avg_price * USD_TO_RMB * 0.25, 8)
    return SupplierScoreInput(
        product_name=product.product_name,
        supplier_count_1688=supplier_count,
        avg_supplier_moq=moq,
        min_unit_cost_rmb=round(unit_cost * 0.9, 2),
        max_unit_cost_rmb=round(unit_cost * 1.25, 2),
        mold_complexity=complexity,
        packaging_complexity=packaging_complexity,
        supply_chain_maturity=85 if supplier_count >= 80 else 65 if supplier_count >= 40 else 45,
    )


def estimated_moq(product: SeedProduct) -> int:
    if product.avg_price <= 20:
        return 200
    if product.avg_price <= 40:
        return 300
    if product.avg_price <= 60:
        return 500
    return 800


def packaging_cost_per_unit(product: SeedProduct) -> float:
    if product.is_fragile:
        return 8
    if product.weight_kg is not None and product.weight_kg > 1:
        return 6
    return 3


def estimated_cpc(product: SeedProduct) -> float:
    if product.sponsored_density > 0.50:
        return 2.4
    if product.sponsored_density > 0.35:
        return 1.4
    if product.sponsored_density > 0.20:
        return 0.8
    return 0.45


def build_key_opportunities(scanned: ScannedProduct) -> list[str]:
    opportunities: list[str] = []
    if ProductTag.STRONG_OPPORTUNITY in scanned.tags:
        opportunities.append("Low review + easy launch candidate")
    if ProductTag.LOW_REVIEW in scanned.tags:
        opportunities.append("Top10 has low-review entry points")
    if ProductTag.HIGH_MARGIN in scanned.tags:
        opportunities.append("Price range leaves room for margin")
    return opportunities or ["Researchable product direction"]
