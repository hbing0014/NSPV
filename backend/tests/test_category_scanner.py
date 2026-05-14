from app.services.discovery.category_scanner import scan_products
from app.services.discovery.rules import ProductLayer, ProductTag, ScannerRuleConfig, evaluate_product
from app.services.discovery.seed_products import load_seed_products


def product_by_asin(asin: str):
    return next(product for product in load_seed_products() if product.asin == asin)


def test_low_price_products_are_rejected() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVH00007"))

    assert evaluation.layer == ProductLayer.REJECTED
    assert ProductTag.LOW_PRICE in evaluation.tags
    assert any("below $15" in reason for reason in evaluation.rejection_reasons)


def test_high_price_products_are_rejected_by_default() -> None:
    product = product_by_asin("NSPVK00001").model_copy(update={"avg_price": 89.99})
    evaluation = evaluate_product(product)

    assert evaluation.layer == ProductLayer.REJECTED
    assert ProductTag.HIGH_PRICE in evaluation.tags
    assert any("above $80" in reason for reason in evaluation.rejection_reasons)


def test_high_review_red_ocean_products_are_rejected() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVS00010"))

    assert evaluation.layer == ProductLayer.REJECTED
    assert ProductTag.RED_OCEAN in evaluation.tags
    assert ProductTag.REVIEW_BARRIER in evaluation.tags


def test_amazon_basics_products_are_rejected_by_default() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVH00003"))

    assert evaluation.layer == ProductLayer.REJECTED
    assert ProductTag.AMAZON_BASICS in evaluation.tags
    assert any("Amazon Basics" in reason for reason in evaluation.rejection_reasons)


def test_heavy_products_are_rejected_by_default() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVK00005"))

    assert evaluation.layer == ProductLayer.REJECTED
    assert ProductTag.HEAVY in evaluation.tags
    assert any("exceeds 1kg" in reason for reason in evaluation.rejection_reasons)


def test_fragile_products_are_rejected_by_default() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVK00006"))

    assert evaluation.layer == ProductLayer.REJECTED
    assert ProductTag.FRAGILE in evaluation.tags
    assert any("fragile" in reason.lower() for reason in evaluation.rejection_reasons)


def test_seasonal_products_are_rejected_by_default() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVK00009"))

    assert evaluation.layer == ProductLayer.REJECTED
    assert ProductTag.SEASONAL in evaluation.tags
    assert any("Seasonality" in reason for reason in evaluation.rejection_reasons)


def test_sponsored_density_generates_high_ppc_warning() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVK00007"))

    assert ProductTag.HIGH_PPC in evaluation.tags
    assert any("PPC pressure" in warning for warning in evaluation.warnings)


def test_rating_and_low_review_generate_low_risk_tag() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVK00001"))

    assert ProductTag.LOW_RISK in evaluation.tags
    assert ProductTag.LOW_REVIEW in evaluation.tags


def test_low_review_good_fit_products_enter_opportunity_layer() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVK00001"))

    assert evaluation.layer == ProductLayer.OPPORTUNITY
    assert ProductTag.STRONG_OPPORTUNITY in evaluation.tags
    assert evaluation.rejection_reasons == []


def test_medium_risk_products_enter_research_layer() -> None:
    evaluation = evaluate_product(product_by_asin("NSPVS00007"))

    assert evaluation.layer == ProductLayer.RESEARCH
    assert evaluation.rejection_reasons == []
    assert evaluation.warnings


def test_rules_can_be_relaxed_for_manual_research() -> None:
    config = ScannerRuleConfig(exclude_amazon_basics=False, exclude_red_ocean=False)
    evaluation = evaluate_product(product_by_asin("NSPVS00002"), config=config)

    assert evaluation.layer == ProductLayer.RESEARCH
    assert ProductTag.AMAZON_BASICS in evaluation.tags
    assert ProductTag.RED_OCEAN in evaluation.tags
    assert evaluation.rejection_reasons == []


def test_scan_products_partitions_all_layers() -> None:
    result = scan_products()

    assert result.total_products_scanned == 30
    assert len(result.rejected) > 0
    assert len(result.research) > 0
    assert len(result.opportunities) > 0
    assert result.total_products_filtered == len(result.rejected)


def test_scan_products_can_filter_by_category() -> None:
    result = scan_products(category="Kitchen & Dining")

    assert result.total_products_scanned == 10
    assert all(product.product.category == "Kitchen & Dining" for product in result.products)


def test_opportunity_products_do_not_include_default_hard_filter_failures() -> None:
    result = scan_products()

    for scanned in result.opportunities:
        assert scanned.product.avg_price >= 15
        assert scanned.product.avg_price <= 80
        assert scanned.product.avg_reviews_top10 <= 1500
        assert scanned.product.amazon_basics_present is False
        assert scanned.product.weight_kg is not None
        assert scanned.product.weight_kg <= 1
        assert scanned.product.is_fragile is False
        assert scanned.product.seasonality_score <= 0.7
        assert scanned.evaluation.rejection_reasons == []


def test_every_seed_product_has_explainable_tags_or_reasons() -> None:
    result = scan_products()

    for scanned in result.products:
        assert scanned.tags or scanned.evaluation.rejection_reasons or scanned.evaluation.warnings
