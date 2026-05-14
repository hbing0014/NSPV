from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal


ComplexityLevel = Literal["low", "medium", "high"]


class SupplierTag(StrEnum):
    MANY_SUPPLIERS = "MANY_SUPPLIERS"
    LOW_MOQ = "LOW_MOQ"
    MATURE_SUPPLY_CHAIN = "MATURE_SUPPLY_CHAIN"
    HIGH_MOQ = "HIGH_MOQ"
    MOLD_COMPLEX = "MOLD_COMPLEX"
    PACKAGING_COMPLEX = "PACKAGING_COMPLEX"
    LOW_SUPPLIER_COUNT = "LOW_SUPPLIER_COUNT"
    BEGINNER_SUPPLIER_FRIENDLY = "BEGINNER_SUPPLIER_FRIENDLY"


@dataclass(frozen=True)
class SupplierScoreInput:
    product_name: str
    supplier_count_1688: int
    avg_supplier_moq: int
    min_unit_cost_rmb: float
    max_unit_cost_rmb: float
    mold_complexity: ComplexityLevel
    packaging_complexity: ComplexityLevel
    supply_chain_maturity: float


@dataclass(frozen=True)
class SupplierScoreResult:
    supplier_score: float
    supplier_count_score: float
    moq_score: float
    price_stability_score: float
    mold_score: float
    packaging_score: float
    maturity_score: float
    level: str
    tags: list[SupplierTag] = field(default_factory=list)


def calculate_supplier_score(data: SupplierScoreInput) -> SupplierScoreResult:
    supplier_count_score = score_supplier_count(data.supplier_count_1688)
    moq_score = score_supplier_moq(data.avg_supplier_moq)
    price_stability_score = score_price_stability(data.min_unit_cost_rmb, data.max_unit_cost_rmb)
    mold_score = score_complexity(data.mold_complexity)
    packaging_score = score_complexity(data.packaging_complexity)
    maturity_score = clamp(data.supply_chain_maturity)

    supplier_score = round(
        supplier_count_score * 0.20
        + moq_score * 0.25
        + price_stability_score * 0.15
        + mold_score * 0.15
        + packaging_score * 0.10
        + maturity_score * 0.15,
        2,
    )
    return SupplierScoreResult(
        supplier_score=supplier_score,
        supplier_count_score=supplier_count_score,
        moq_score=moq_score,
        price_stability_score=price_stability_score,
        mold_score=mold_score,
        packaging_score=packaging_score,
        maturity_score=maturity_score,
        level=supplier_level(supplier_score),
        tags=supplier_tags(data, supplier_score, supplier_count_score, moq_score, mold_score, packaging_score, maturity_score),
    )


def score_supplier_count(supplier_count: int) -> float:
    if supplier_count >= 80:
        return 95
    if supplier_count >= 40:
        return 85
    if supplier_count >= 20:
        return 70
    if supplier_count >= 8:
        return 45
    return 20


def score_supplier_moq(avg_supplier_moq: int) -> float:
    if avg_supplier_moq <= 200:
        return 95
    if avg_supplier_moq <= 500:
        return 85
    if avg_supplier_moq <= 1000:
        return 65
    if avg_supplier_moq <= 3000:
        return 35
    return 15


def score_price_stability(min_unit_cost_rmb: float, max_unit_cost_rmb: float) -> float:
    if min_unit_cost_rmb <= 0 or max_unit_cost_rmb <= 0 or max_unit_cost_rmb < min_unit_cost_rmb:
        return 30
    spread = (max_unit_cost_rmb - min_unit_cost_rmb) / min_unit_cost_rmb
    if spread <= 0.20:
        return 90
    if spread <= 0.50:
        return 75
    if spread <= 1.00:
        return 55
    return 30


def score_complexity(level: ComplexityLevel) -> float:
    scores = {
        "low": 90,
        "medium": 65,
        "high": 30,
    }
    return scores[level]


def supplier_level(score: float) -> str:
    if score >= 85:
        return "Beginner-Friendly Supply"
    if score >= 70:
        return "Researchable Supply"
    if score >= 55:
        return "Supply Risk Needs Review"
    return "Poor Supplier Fit"


def supplier_tags(
    data: SupplierScoreInput,
    supplier_score: float,
    supplier_count_score: float,
    moq_score: float,
    mold_score: float,
    packaging_score: float,
    maturity_score: float,
) -> list[SupplierTag]:
    tags: list[SupplierTag] = []
    if supplier_count_score >= 85:
        tags.append(SupplierTag.MANY_SUPPLIERS)
    if moq_score >= 85:
        tags.append(SupplierTag.LOW_MOQ)
    if maturity_score >= 80:
        tags.append(SupplierTag.MATURE_SUPPLY_CHAIN)
    if data.avg_supplier_moq > 1000:
        tags.append(SupplierTag.HIGH_MOQ)
    if mold_score < 50:
        tags.append(SupplierTag.MOLD_COMPLEX)
    if packaging_score < 50:
        tags.append(SupplierTag.PACKAGING_COMPLEX)
    if data.supplier_count_1688 < 8:
        tags.append(SupplierTag.LOW_SUPPLIER_COUNT)
    if supplier_score >= 85 and not any(tag in tags for tag in risk_tags()):
        tags.append(SupplierTag.BEGINNER_SUPPLIER_FRIENDLY)
    return tags


def risk_tags() -> set[SupplierTag]:
    return {
        SupplierTag.HIGH_MOQ,
        SupplierTag.MOLD_COMPLEX,
        SupplierTag.PACKAGING_COMPLEX,
        SupplierTag.LOW_SUPPLIER_COUNT,
    }


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))
