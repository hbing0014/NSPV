from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal


CustomizationLevel = Literal["white_label", "simple_label", "light_custom", "mold_development"]


class LaunchTag(StrEnum):
    LOW_BUDGET_FRIENDLY = "LOW_BUDGET_FRIENDLY"
    HIGH_PPC_RISK = "HIGH_PPC_RISK"
    HIGH_MOQ = "HIGH_MOQ"
    INVENTORY_HEAVY = "INVENTORY_HEAVY"
    REVIEW_BARRIER = "REVIEW_BARRIER"
    OPERATION_COMPLEX = "OPERATION_COMPLEX"
    BEGINNER_FRIENDLY = "BEGINNER_FRIENDLY"


@dataclass(frozen=True)
class LaunchScoreInput:
    product_name: str
    user_budget_rmb: float
    estimated_unit_cost_rmb: float
    estimated_first_order_qty: int
    estimated_shipping_cost_rmb: float
    estimated_packaging_cost_rmb: float
    estimated_ppc_seed_budget_rmb: float
    avg_cpc_usd: float
    sponsored_density: float
    min_reviews_top10: int
    avg_supplier_moq: int
    customization_level: CustomizationLevel
    estimated_monthly_sales: int
    weight_kg: float | None
    is_fragile: bool = False
    variation_count: int = 1
    high_return_risk: bool = False
    complex_installation: bool = False


@dataclass(frozen=True)
class LaunchBudgetBreakdown:
    first_order_budget: float
    shipping_budget: float
    packaging_budget: float
    ppc_seed_budget: float
    buffer_budget: float
    total_budget: float


@dataclass(frozen=True)
class LaunchScoreResult:
    launch_score: float
    budget_score: float
    ppc_score: float
    review_score: float
    moq_score: float
    inventory_score: float
    operations_score: float
    estimated_total_launch_budget: float
    estimated_launch_days: int
    estimated_break_even_days: int
    level: str
    tags: list[LaunchTag] = field(default_factory=list)
    budget_breakdown: LaunchBudgetBreakdown | None = None


def calculate_launch_score(data: LaunchScoreInput) -> LaunchScoreResult:
    budget = build_budget_breakdown(data)
    budget_score = score_budget_feasibility(budget.total_budget, data.user_budget_rmb)
    ppc_score = score_ppc_difficulty(data.avg_cpc_usd, data.sponsored_density)
    review_score = score_review_difficulty(data.min_reviews_top10)
    moq_score = score_moq_accessibility(data.avg_supplier_moq, data.customization_level)
    inventory_score = score_inventory_pressure(data.estimated_first_order_qty, data.estimated_monthly_sales)
    operations_score = score_operational_complexity(
        weight_kg=data.weight_kg,
        is_fragile=data.is_fragile,
        variation_count=data.variation_count,
        high_return_risk=data.high_return_risk,
        complex_installation=data.complex_installation,
    )

    launch_score = round(
        budget_score * 0.30
        + ppc_score * 0.20
        + review_score * 0.15
        + moq_score * 0.15
        + inventory_score * 0.10
        + operations_score * 0.10,
        2,
    )
    return LaunchScoreResult(
        launch_score=launch_score,
        budget_score=budget_score,
        ppc_score=ppc_score,
        review_score=review_score,
        moq_score=moq_score,
        inventory_score=inventory_score,
        operations_score=operations_score,
        estimated_total_launch_budget=budget.total_budget,
        estimated_launch_days=estimate_launch_days(data),
        estimated_break_even_days=estimate_break_even_days(data),
        level=launch_level(launch_score),
        tags=launch_tags(data, launch_score, budget_score, ppc_score, review_score, moq_score, inventory_score, operations_score),
        budget_breakdown=budget,
    )


def build_budget_breakdown(data: LaunchScoreInput) -> LaunchBudgetBreakdown:
    first_order_budget = data.estimated_unit_cost_rmb * data.estimated_first_order_qty
    subtotal = (
        first_order_budget
        + data.estimated_shipping_cost_rmb
        + data.estimated_packaging_cost_rmb
        + data.estimated_ppc_seed_budget_rmb
    )
    buffer_budget = round(subtotal * 0.20, 2)
    return LaunchBudgetBreakdown(
        first_order_budget=round(first_order_budget, 2),
        shipping_budget=round(data.estimated_shipping_cost_rmb, 2),
        packaging_budget=round(data.estimated_packaging_cost_rmb, 2),
        ppc_seed_budget=round(data.estimated_ppc_seed_budget_rmb, 2),
        buffer_budget=buffer_budget,
        total_budget=round(subtotal + buffer_budget, 2),
    )


def score_budget_feasibility(total_launch_budget: float, user_budget_rmb: float) -> float:
    if user_budget_rmb <= 0:
        return 0
    ratio = total_launch_budget / user_budget_rmb
    if ratio <= 0.30:
        return 95
    if ratio <= 0.50:
        return 85
    if ratio <= 0.70:
        return 65
    if ratio <= 0.90:
        return 40
    return 15


def score_ppc_difficulty(avg_cpc_usd: float, sponsored_density: float) -> float:
    if avg_cpc_usd < 0.5:
        score = 95
    elif avg_cpc_usd < 1:
        score = 80
    elif avg_cpc_usd < 2:
        score = 60
    elif avg_cpc_usd < 3:
        score = 35
    else:
        score = 15

    if sponsored_density < 0.20:
        score += 10
    elif sponsored_density > 0.60:
        score -= 20
    elif sponsored_density > 0.40:
        score -= 10
    return clamp(score)


def score_review_difficulty(min_reviews_top10: int) -> float:
    if min_reviews_top10 < 50:
        return 95
    if min_reviews_top10 <= 150:
        return 85
    if min_reviews_top10 <= 300:
        return 70
    if min_reviews_top10 <= 800:
        return 45
    return 20


def score_moq_accessibility(avg_supplier_moq: int, customization_level: CustomizationLevel) -> float:
    if avg_supplier_moq <= 200:
        score = 95
    elif avg_supplier_moq <= 500:
        score = 85
    elif avg_supplier_moq <= 1000:
        score = 65
    elif avg_supplier_moq <= 3000:
        score = 35
    else:
        score = 15

    modifiers = {
        "white_label": 10,
        "simple_label": 5,
        "light_custom": 0,
        "mold_development": -20,
    }
    return clamp(score + modifiers[customization_level])


def score_inventory_pressure(first_order_qty: int, estimated_monthly_sales: int) -> float:
    days = inventory_cycle_days(first_order_qty, estimated_monthly_sales)
    if days < 45:
        return 95
    if days <= 75:
        return 85
    if days <= 120:
        return 60
    if days <= 180:
        return 35
    return 10


def score_operational_complexity(
    weight_kg: float | None,
    is_fragile: bool,
    variation_count: int,
    high_return_risk: bool,
    complex_installation: bool,
) -> float:
    if is_fragile:
        score = 25
    elif weight_kg is not None and weight_kg > 1:
        score = 40
    elif weight_kg is not None and weight_kg <= 0.5:
        score = 90
    else:
        score = 75

    if variation_count > 3:
        score -= 10
    if high_return_risk:
        score -= 15
    if complex_installation:
        score -= 15
    return clamp(score)


def inventory_cycle_days(first_order_qty: int, estimated_monthly_sales: int) -> int:
    if estimated_monthly_sales <= 0:
        return 999
    return round((first_order_qty / estimated_monthly_sales) * 30)


def estimate_launch_days(data: LaunchScoreInput) -> int:
    base_days = 30
    customization_days = {
        "white_label": 0,
        "simple_label": 5,
        "light_custom": 15,
        "mold_development": 45,
    }[data.customization_level]
    inventory_days = min(inventory_cycle_days(data.estimated_first_order_qty, data.estimated_monthly_sales), 120)
    return int(base_days + customization_days + inventory_days * 0.25)


def estimate_break_even_days(data: LaunchScoreInput) -> int:
    gross_profit_per_unit = max(data.estimated_unit_cost_rmb * 0.75, 1)
    units_to_cover_ppc = data.estimated_ppc_seed_budget_rmb / gross_profit_per_unit
    monthly_sales = max(data.estimated_monthly_sales, 1)
    return round((units_to_cover_ppc / monthly_sales) * 30 + 30)


def launch_level(score: float) -> str:
    if score >= 90:
        return "Excellent Launch Product"
    if score >= 80:
        return "Strong Launch Candidate"
    if score >= 70:
        return "Launchable with Caution"
    if score >= 60:
        return "Difficult for Beginners"
    return "Poor Launch Fit"


def launch_tags(
    data: LaunchScoreInput,
    launch_score: float,
    budget_score: float,
    ppc_score: float,
    review_score: float,
    moq_score: float,
    inventory_score: float,
    operations_score: float,
) -> list[LaunchTag]:
    tags: list[LaunchTag] = []
    if budget_score >= 85:
        tags.append(LaunchTag.LOW_BUDGET_FRIENDLY)
    if ppc_score < 50:
        tags.append(LaunchTag.HIGH_PPC_RISK)
    if data.avg_supplier_moq > 1000 or moq_score < 50:
        tags.append(LaunchTag.HIGH_MOQ)
    if inventory_score < 60:
        tags.append(LaunchTag.INVENTORY_HEAVY)
    if review_score < 60:
        tags.append(LaunchTag.REVIEW_BARRIER)
    if operations_score < 60:
        tags.append(LaunchTag.OPERATION_COMPLEX)
    if launch_score >= 80 and not any(tag in tags for tag in risk_tags()):
        tags.append(LaunchTag.BEGINNER_FRIENDLY)
    return tags


def risk_tags() -> set[LaunchTag]:
    return {
        LaunchTag.HIGH_PPC_RISK,
        LaunchTag.HIGH_MOQ,
        LaunchTag.INVENTORY_HEAVY,
        LaunchTag.REVIEW_BARRIER,
        LaunchTag.OPERATION_COMPLEX,
    }


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))
