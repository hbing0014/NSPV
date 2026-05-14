from dataclasses import dataclass, field
from enum import StrEnum

from app.services.discovery.seed_products import SeedProduct


class ProductLayer(StrEnum):
    REJECTED = "Rejected"
    RESEARCH = "Research"
    OPPORTUNITY = "Opportunity"


class ProductTag(StrEnum):
    LOW_REVIEW = "LOW_REVIEW"
    LOW_RISK = "LOW_RISK"
    HIGH_MARGIN = "HIGH_MARGIN"
    HIGH_PPC = "HIGH_PPC"
    RED_OCEAN = "RED_OCEAN"
    AMAZON_BASICS = "AMAZON_BASICS"
    HEAVY = "HEAVY"
    FRAGILE = "FRAGILE"
    SEASONAL = "SEASONAL"
    STRONG_OPPORTUNITY = "STRONG_OPPORTUNITY"
    LOW_PRICE = "LOW_PRICE"
    HIGH_PRICE = "HIGH_PRICE"
    MATURE_MARKET = "MATURE_MARKET"
    REVIEW_BARRIER = "REVIEW_BARRIER"
    PATENT_RISK = "PATENT_RISK"


@dataclass(frozen=True)
class ScannerRuleConfig:
    min_price: float = 15
    max_price: float = 80
    max_avg_reviews_top10: float = 1500
    max_weight_kg: float = 1
    max_seasonality_score: float = 0.7
    exclude_amazon_basics: bool = True
    exclude_fragile: bool = True
    exclude_seasonal: bool = True
    exclude_heavy: bool = True
    exclude_red_ocean: bool = True


@dataclass(frozen=True)
class RuleEvaluation:
    asin: str
    product_name: str
    layer: ProductLayer
    tags: list[ProductTag] = field(default_factory=list)
    rejection_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_rejected(self) -> bool:
        return self.layer == ProductLayer.REJECTED


def evaluate_product(product: SeedProduct, config: ScannerRuleConfig | None = None) -> RuleEvaluation:
    rule_config = config or ScannerRuleConfig()
    tags: list[ProductTag] = []
    rejection_reasons: list[str] = []
    warnings: list[str] = []

    apply_price_rules(product, rule_config, tags, rejection_reasons)
    apply_review_rules(product, rule_config, tags, rejection_reasons, warnings)
    apply_amazon_basics_rule(product, rule_config, tags, rejection_reasons)
    apply_weight_rule(product, rule_config, tags, rejection_reasons)
    apply_fragile_rule(product, rule_config, tags, rejection_reasons)
    apply_seasonality_rule(product, rule_config, tags, rejection_reasons)
    apply_patent_risk_rule(product, tags, warnings)
    apply_soft_rules(product, tags, warnings)

    layer = determine_layer(tags, rejection_reasons)
    return RuleEvaluation(
        asin=product.asin,
        product_name=product.product_name,
        layer=layer,
        tags=dedupe_tags(tags),
        rejection_reasons=rejection_reasons,
        warnings=warnings,
    )


def apply_price_rules(
    product: SeedProduct,
    config: ScannerRuleConfig,
    tags: list[ProductTag],
    rejection_reasons: list[str],
) -> None:
    if product.avg_price < config.min_price:
        tags.append(ProductTag.LOW_PRICE)
        rejection_reasons.append("Avg price is below $15, margin and ad room are too limited.")
    if product.avg_price > config.max_price:
        tags.append(ProductTag.HIGH_PRICE)
        rejection_reasons.append("Avg price is above $80, cold-start purchase conversion risk is high.")
    if 20 <= product.avg_price <= 40:
        tags.append(ProductTag.HIGH_MARGIN)


def apply_review_rules(
    product: SeedProduct,
    config: ScannerRuleConfig,
    tags: list[ProductTag],
    rejection_reasons: list[str],
    warnings: list[str],
) -> None:
    if product.avg_reviews_top10 > config.max_avg_reviews_top10:
        tags.extend([ProductTag.RED_OCEAN, ProductTag.REVIEW_BARRIER])
        if config.exclude_red_ocean:
            rejection_reasons.append("Top10 average reviews exceed 1500, review barrier is too high.")
        else:
            warnings.append("Top10 average reviews exceed 1500.")
    elif product.avg_reviews_top10 >= 800:
        warnings.append("Top10 average reviews are in the medium-risk range.")

    if product.min_reviews_top10 < 150:
        tags.append(ProductTag.LOW_REVIEW)


def apply_amazon_basics_rule(
    product: SeedProduct,
    config: ScannerRuleConfig,
    tags: list[ProductTag],
    rejection_reasons: list[str],
) -> None:
    if product.amazon_basics_present:
        tags.append(ProductTag.AMAZON_BASICS)
        if config.exclude_amazon_basics:
            rejection_reasons.append("Amazon Basics is present in the market.")


def apply_weight_rule(
    product: SeedProduct,
    config: ScannerRuleConfig,
    tags: list[ProductTag],
    rejection_reasons: list[str],
) -> None:
    if product.weight_kg is None:
        return
    if product.weight_kg > config.max_weight_kg:
        tags.append(ProductTag.HEAVY)
        if config.exclude_heavy:
            rejection_reasons.append("Product weight exceeds 1kg, FBA and logistics risk are high.")


def apply_fragile_rule(
    product: SeedProduct,
    config: ScannerRuleConfig,
    tags: list[ProductTag],
    rejection_reasons: list[str],
) -> None:
    if product.is_fragile:
        tags.append(ProductTag.FRAGILE)
        if config.exclude_fragile:
            rejection_reasons.append("Product is fragile, return and packaging risk are high.")


def apply_seasonality_rule(
    product: SeedProduct,
    config: ScannerRuleConfig,
    tags: list[ProductTag],
    rejection_reasons: list[str],
) -> None:
    if product.seasonality_score > config.max_seasonality_score:
        tags.append(ProductTag.SEASONAL)
        if config.exclude_seasonal:
            rejection_reasons.append("Seasonality score is high, inventory timing risk is high.")


def apply_patent_risk_rule(product: SeedProduct, tags: list[ProductTag], warnings: list[str]) -> None:
    if product.patent_risk_level == "high":
        tags.append(ProductTag.PATENT_RISK)
        warnings.append("Patent risk is high and needs manual review.")
    elif product.patent_risk_level == "medium":
        warnings.append("Patent risk is medium and should be reviewed before sourcing.")


def apply_soft_rules(product: SeedProduct, tags: list[ProductTag], warnings: list[str]) -> None:
    if product.sponsored_density > 0.50:
        tags.append(ProductTag.HIGH_PPC)
        warnings.append("Sponsored density is above 50%, PPC pressure is high.")
    elif product.sponsored_density >= 0.30:
        warnings.append("Sponsored density is in the medium-risk range.")

    if product.avg_rating > 4.8:
        tags.append(ProductTag.MATURE_MARKET)
        warnings.append("Average rating is very high, differentiation may be harder.")
    elif 4.2 <= product.avg_rating <= 4.7 and product.min_reviews_top10 < 150:
        tags.append(ProductTag.LOW_RISK)

    if is_strong_opportunity(product):
        tags.append(ProductTag.STRONG_OPPORTUNITY)


def is_strong_opportunity(product: SeedProduct) -> bool:
    return (
        20 <= product.avg_price <= 40
        and product.avg_reviews_top10 < 800
        and product.min_reviews_top10 < 150
        and product.sponsored_density < 0.35
        and not product.amazon_basics_present
        and product.weight_kg is not None
        and product.weight_kg < 0.5
        and not product.is_fragile
        and product.seasonality_score <= 0.7
    )


def determine_layer(tags: list[ProductTag], rejection_reasons: list[str]) -> ProductLayer:
    if rejection_reasons:
        return ProductLayer.REJECTED
    if ProductTag.STRONG_OPPORTUNITY in tags:
        return ProductLayer.OPPORTUNITY
    return ProductLayer.RESEARCH


def dedupe_tags(tags: list[ProductTag]) -> list[ProductTag]:
    return list(dict.fromkeys(tags))
