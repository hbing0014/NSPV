from dataclasses import dataclass, field
from enum import StrEnum


class NPFSRecommendation(StrEnum):
    STRONGLY_RECOMMENDED = "strongly_recommended"
    WORTH_RESEARCH = "worth_research"
    CAUTION = "caution"
    AVOID = "avoid"


class NPFSRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class NPFSInput:
    demand_score: float
    competition_score: float
    profit_score: float
    opportunity_score: float
    launch_score: float
    supplier_score: float
    warnings: list[str] = field(default_factory=list)
    is_red_ocean: bool = False
    is_amazon_basics: bool = False
    is_fragile: bool = False
    is_heavy: bool = False
    is_patent_risk: bool = False


@dataclass(frozen=True)
class NPFSResult:
    npfs_score: float
    recommendation: NPFSRecommendation
    risk_level: NPFSRiskLevel
    weighted_scores: dict[str, float]
    warnings: list[str] = field(default_factory=list)


def calculate_npfs(data: NPFSInput) -> NPFSResult:
    weighted_scores = {
        "demand": clamp(data.demand_score) * 0.20,
        "competition": clamp(data.competition_score) * 0.25,
        "profit": clamp(data.profit_score) * 0.20,
        "opportunity": clamp(data.opportunity_score) * 0.15,
        "launch": clamp(data.launch_score) * 0.10,
        "supplier": clamp(data.supplier_score) * 0.10,
    }
    npfs_score = round(sum(weighted_scores.values()), 2)
    warnings = normalized_warnings(data)
    return NPFSResult(
        npfs_score=npfs_score,
        recommendation=recommendation_for_npfs(npfs_score),
        risk_level=risk_level_for_npfs(npfs_score, warnings),
        weighted_scores={key: round(value, 2) for key, value in weighted_scores.items()},
        warnings=warnings,
    )


def recommendation_for_npfs(score: float) -> NPFSRecommendation:
    if score >= 85:
        return NPFSRecommendation.STRONGLY_RECOMMENDED
    if score >= 70:
        return NPFSRecommendation.WORTH_RESEARCH
    if score >= 50:
        return NPFSRecommendation.CAUTION
    return NPFSRecommendation.AVOID


def risk_level_for_npfs(score: float, warnings: list[str]) -> NPFSRiskLevel:
    if score < 50 or len(warnings) >= 3:
        return NPFSRiskLevel.HIGH
    if score < 70 or warnings:
        return NPFSRiskLevel.MEDIUM
    return NPFSRiskLevel.LOW


def normalized_warnings(data: NPFSInput) -> list[str]:
    warnings = list(data.warnings)
    if data.is_red_ocean:
        warnings.append("Red ocean market risk detected.")
    if data.is_amazon_basics:
        warnings.append("Amazon Basics competition risk detected.")
    if data.is_fragile:
        warnings.append("Fragile product operational risk detected.")
    if data.is_heavy:
        warnings.append("Heavy product logistics risk detected.")
    if data.is_patent_risk:
        warnings.append("Patent risk needs manual review.")
    return dedupe(warnings)


def dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))
