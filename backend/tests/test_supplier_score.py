from app.services.discovery.supplier_score import (
    SupplierScoreInput,
    SupplierTag,
    calculate_supplier_score,
    score_price_stability,
    score_supplier_count,
    score_supplier_moq,
)


def beginner_friendly_input() -> SupplierScoreInput:
    return SupplierScoreInput(
        product_name="Under Sink Organizer",
        supplier_count_1688=95,
        avg_supplier_moq=200,
        min_unit_cost_rmb=35,
        max_unit_cost_rmb=42,
        mold_complexity="low",
        packaging_complexity="low",
        supply_chain_maturity=88,
    )


def high_risk_input() -> SupplierScoreInput:
    return SupplierScoreInput(
        product_name="Custom Air Fryer Accessory Set",
        supplier_count_1688=5,
        avg_supplier_moq=3000,
        min_unit_cost_rmb=40,
        max_unit_cost_rmb=95,
        mold_complexity="high",
        packaging_complexity="high",
        supply_chain_maturity=35,
    )


def test_supplier_count_thresholds() -> None:
    assert score_supplier_count(80) == 95
    assert score_supplier_count(40) == 85
    assert score_supplier_count(20) == 70
    assert score_supplier_count(8) == 45
    assert score_supplier_count(7) == 20


def test_supplier_moq_thresholds() -> None:
    assert score_supplier_moq(200) == 95
    assert score_supplier_moq(500) == 85
    assert score_supplier_moq(1000) == 65
    assert score_supplier_moq(3000) == 35
    assert score_supplier_moq(3001) == 15


def test_price_stability_score_uses_supplier_price_spread() -> None:
    assert score_price_stability(10, 12) == 90
    assert score_price_stability(10, 15) == 75
    assert score_price_stability(10, 20) == 55
    assert score_price_stability(10, 21) == 30
    assert score_price_stability(0, 10) == 30


def test_low_moq_standard_product_scores_high() -> None:
    result = calculate_supplier_score(beginner_friendly_input())

    assert result.supplier_score >= 85
    assert result.level == "Beginner-Friendly Supply"
    assert SupplierTag.MANY_SUPPLIERS in result.tags
    assert SupplierTag.LOW_MOQ in result.tags
    assert SupplierTag.MATURE_SUPPLY_CHAIN in result.tags
    assert SupplierTag.BEGINNER_SUPPLIER_FRIENDLY in result.tags


def test_high_moq_mold_complex_product_scores_low() -> None:
    result = calculate_supplier_score(high_risk_input())

    assert result.supplier_score < 55
    assert result.level == "Poor Supplier Fit"
    assert SupplierTag.HIGH_MOQ in result.tags
    assert SupplierTag.MOLD_COMPLEX in result.tags
    assert SupplierTag.PACKAGING_COMPLEX in result.tags
    assert SupplierTag.LOW_SUPPLIER_COUNT in result.tags


def test_supplier_score_outputs_all_subscores() -> None:
    result = calculate_supplier_score(beginner_friendly_input())

    assert result.supplier_score > 0
    assert result.supplier_count_score > 0
    assert result.moq_score > 0
    assert result.price_stability_score > 0
    assert result.mold_score > 0
    assert result.packaging_score > 0
    assert result.maturity_score > 0
