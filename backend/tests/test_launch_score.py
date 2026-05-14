from app.services.discovery.launch_score import (
    LaunchTag,
    LaunchScoreInput,
    calculate_launch_score,
    inventory_cycle_days,
    score_budget_feasibility,
    score_inventory_pressure,
    score_moq_accessibility,
    score_operational_complexity,
    score_ppc_difficulty,
    score_review_difficulty,
)


def sink_organizer_input() -> LaunchScoreInput:
    return LaunchScoreInput(
        product_name="Sink Organizer",
        user_budget_rmb=100000,
        estimated_unit_cost_rmb=45,
        estimated_first_order_qty=300,
        estimated_shipping_cost_rmb=5000,
        estimated_packaging_cost_rmb=1500,
        estimated_ppc_seed_budget_rmb=7000,
        avg_cpc_usd=0.75,
        sponsored_density=0.28,
        min_reviews_top10=88,
        avg_supplier_moq=300,
        customization_level="simple_label",
        estimated_monthly_sales=900,
        weight_kg=0.48,
    )


def air_fryer_accessory_input() -> LaunchScoreInput:
    return LaunchScoreInput(
        product_name="Air Fryer Accessory Set",
        user_budget_rmb=50000,
        estimated_unit_cost_rmb=70,
        estimated_first_order_qty=1200,
        estimated_shipping_cost_rmb=18000,
        estimated_packaging_cost_rmb=5000,
        estimated_ppc_seed_budget_rmb=18000,
        avg_cpc_usd=2.4,
        sponsored_density=0.64,
        min_reviews_top10=540,
        avg_supplier_moq=2000,
        customization_level="mold_development",
        estimated_monthly_sales=260,
        weight_kg=1.2,
        variation_count=6,
        high_return_risk=True,
        complex_installation=True,
    )


def test_budget_feasibility_thresholds() -> None:
    assert score_budget_feasibility(30000, 100000) == 95
    assert score_budget_feasibility(50000, 100000) == 85
    assert score_budget_feasibility(70000, 100000) == 65
    assert score_budget_feasibility(90000, 100000) == 40
    assert score_budget_feasibility(91000, 100000) == 15


def test_ppc_score_uses_cpc_and_sponsored_density_adjustment() -> None:
    assert score_ppc_difficulty(0.45, 0.10) == 100
    assert score_ppc_difficulty(0.75, 0.30) == 80
    assert score_ppc_difficulty(1.5, 0.50) == 50
    assert score_ppc_difficulty(3.2, 0.70) == 0


def test_review_difficulty_thresholds() -> None:
    assert score_review_difficulty(49) == 95
    assert score_review_difficulty(150) == 85
    assert score_review_difficulty(300) == 70
    assert score_review_difficulty(800) == 45
    assert score_review_difficulty(801) == 20


def test_moq_accessibility_includes_customization_modifier() -> None:
    assert score_moq_accessibility(200, "white_label") == 100
    assert score_moq_accessibility(500, "simple_label") == 90
    assert score_moq_accessibility(1000, "light_custom") == 65
    assert score_moq_accessibility(2000, "mold_development") == 15


def test_inventory_pressure_uses_inventory_cycle_days() -> None:
    assert inventory_cycle_days(300, 900) == 10
    assert score_inventory_pressure(300, 900) == 95
    assert score_inventory_pressure(1000, 300) == 60
    assert score_inventory_pressure(2000, 300) == 10


def test_operational_complexity_scores_simple_and_complex_products() -> None:
    assert score_operational_complexity(0.4, False, 1, False, False) == 90
    assert score_operational_complexity(1.2, False, 1, False, False) == 40
    assert score_operational_complexity(0.4, True, 5, True, True) == 0


def test_sink_organizer_is_strong_launch_candidate() -> None:
    result = calculate_launch_score(sink_organizer_input())

    assert result.launch_score >= 80
    assert result.level == "Strong Launch Candidate"
    assert result.budget_score == 85
    assert result.review_score == 85
    assert result.moq_score == 90
    assert LaunchTag.LOW_BUDGET_FRIENDLY in result.tags
    assert LaunchTag.BEGINNER_FRIENDLY in result.tags
    assert result.budget_breakdown is not None
    assert result.estimated_total_launch_budget == result.budget_breakdown.total_budget


def test_air_fryer_accessory_set_is_poor_launch_fit() -> None:
    result = calculate_launch_score(air_fryer_accessory_input())

    assert result.launch_score < 60
    assert result.level == "Poor Launch Fit"
    assert LaunchTag.HIGH_PPC_RISK in result.tags
    assert LaunchTag.HIGH_MOQ in result.tags
    assert LaunchTag.INVENTORY_HEAVY in result.tags
    assert LaunchTag.REVIEW_BARRIER in result.tags
    assert LaunchTag.OPERATION_COMPLEX in result.tags


def test_launch_score_outputs_all_subscores_and_budget_fields() -> None:
    result = calculate_launch_score(sink_organizer_input())

    assert result.launch_score > 0
    assert result.budget_score > 0
    assert result.ppc_score > 0
    assert result.review_score > 0
    assert result.moq_score > 0
    assert result.inventory_score > 0
    assert result.operations_score > 0
    assert result.estimated_launch_days > 0
    assert result.estimated_break_even_days > 0
    assert result.budget_breakdown
    assert result.budget_breakdown.first_order_budget == 13500
    assert result.budget_breakdown.buffer_budget > 0
