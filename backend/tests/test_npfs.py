import pytest

from app.services.discovery.npfs import (
    NPFSInput,
    NPFSRecommendation,
    NPFSRiskLevel,
    calculate_npfs,
    recommendation_for_npfs,
    risk_level_for_npfs,
)


def test_npfs_formula_uses_expected_weights() -> None:
    result = calculate_npfs(
        NPFSInput(
            demand_score=80,
            competition_score=70,
            profit_score=90,
            opportunity_score=60,
            launch_score=85,
            supplier_score=75,
        )
    )

    assert result.npfs_score == 76.5
    assert result.weighted_scores == {
        "demand": 16.0,
        "competition": 17.5,
        "profit": 18.0,
        "opportunity": 9.0,
        "launch": 8.5,
        "supplier": 7.5,
    }


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (85, NPFSRecommendation.STRONGLY_RECOMMENDED),
        (70, NPFSRecommendation.WORTH_RESEARCH),
        (50, NPFSRecommendation.CAUTION),
        (49.99, NPFSRecommendation.AVOID),
    ],
)
def test_recommendation_thresholds(score: float, expected: NPFSRecommendation) -> None:
    assert recommendation_for_npfs(score) == expected


def test_npfs_outputs_recommendation_and_low_risk_for_clean_high_score() -> None:
    result = calculate_npfs(
        NPFSInput(
            demand_score=92,
            competition_score=88,
            profit_score=90,
            opportunity_score=86,
            launch_score=91,
            supplier_score=87,
        )
    )

    assert result.npfs_score >= 85
    assert result.recommendation == NPFSRecommendation.STRONGLY_RECOMMENDED
    assert result.risk_level == NPFSRiskLevel.LOW
    assert result.warnings == []


def test_npfs_outputs_medium_risk_when_warnings_exist() -> None:
    result = calculate_npfs(
        NPFSInput(
            demand_score=82,
            competition_score=78,
            profit_score=80,
            opportunity_score=76,
            launch_score=83,
            supplier_score=79,
            is_amazon_basics=True,
        )
    )

    assert result.recommendation == NPFSRecommendation.WORTH_RESEARCH
    assert result.risk_level == NPFSRiskLevel.MEDIUM
    assert "Amazon Basics competition risk detected." in result.warnings


def test_npfs_outputs_high_risk_when_multiple_warnings_exist() -> None:
    result = calculate_npfs(
        NPFSInput(
            demand_score=82,
            competition_score=75,
            profit_score=78,
            opportunity_score=74,
            launch_score=80,
            supplier_score=72,
            is_red_ocean=True,
            is_fragile=True,
            is_heavy=True,
        )
    )

    assert result.npfs_score >= 70
    assert result.risk_level == NPFSRiskLevel.HIGH
    assert len(result.warnings) == 3


def test_low_npfs_is_avoid_and_high_risk() -> None:
    result = calculate_npfs(
        NPFSInput(
            demand_score=35,
            competition_score=30,
            profit_score=45,
            opportunity_score=40,
            launch_score=50,
            supplier_score=42,
        )
    )

    assert result.npfs_score < 50
    assert result.recommendation == NPFSRecommendation.AVOID
    assert result.risk_level == NPFSRiskLevel.HIGH


def test_risk_level_thresholds() -> None:
    assert risk_level_for_npfs(80, []) == NPFSRiskLevel.LOW
    assert risk_level_for_npfs(80, ["warning"]) == NPFSRiskLevel.MEDIUM
    assert risk_level_for_npfs(80, ["a", "b", "c"]) == NPFSRiskLevel.HIGH
    assert risk_level_for_npfs(60, []) == NPFSRiskLevel.MEDIUM
    assert risk_level_for_npfs(49, []) == NPFSRiskLevel.HIGH


def test_npfs_clamps_subscores_before_weighting() -> None:
    result = calculate_npfs(
        NPFSInput(
            demand_score=120,
            competition_score=120,
            profit_score=120,
            opportunity_score=120,
            launch_score=120,
            supplier_score=120,
        )
    )

    assert result.npfs_score == 100
