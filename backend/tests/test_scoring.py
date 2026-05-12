import pytest

from app.schemas.analysis import ProductOut
from app.services.scoring import (
    analyze_products,
    demand_score,
    profit_score,
    recommendation,
    review_competition_score,
    risk_level,
    sponsored_score,
)


@pytest.mark.parametrize(
    ("search_volume", "expected"),
    [
        (50001, 95),
        (20000, 85),
        (10000, 75),
        (5000, 60),
        (4999, 40),
    ],
)
def test_demand_score_thresholds(search_volume: int, expected: float) -> None:
    assert demand_score(search_volume) == expected


@pytest.mark.parametrize(
    ("avg_reviews_top10", "expected"),
    [
        (99, 95),
        (100, 85),
        (300, 65),
        (800, 40),
        (2000, 15),
    ],
)
def test_review_competition_score_thresholds(avg_reviews_top10: float, expected: float) -> None:
    assert review_competition_score(avg_reviews_top10) == expected


@pytest.mark.parametrize(
    ("density", "expected"),
    [
        (0.14, 90),
        (0.15, 70),
        (0.30, 45),
        (0.50, 20),
    ],
)
def test_sponsored_score_thresholds(density: float, expected: float) -> None:
    assert sponsored_score(density) == expected


@pytest.mark.parametrize(
    ("net_margin", "expected"),
    [
        (0.36, 95),
        (0.35, 80),
        (0.25, 80),
        (0.15, 60),
        (0.14, 30),
    ],
)
def test_profit_score_thresholds(net_margin: float, expected: float) -> None:
    assert profit_score(net_margin) == expected


@pytest.mark.parametrize(
    ("nsfs", "expected"),
    [
        (85, "Strongly Recommended"),
        (70, "Worth Research"),
        (50, "Caution"),
        (49.9, "Avoid"),
    ],
)
def test_recommendation_thresholds(nsfs: float, expected: str) -> None:
    assert recommendation(nsfs) == expected


def test_risk_level_uses_score_and_warning_count() -> None:
    assert risk_level(80, []) == "Low"
    assert risk_level(80, ["warning"]) == "Medium"
    assert risk_level(80, ["a", "b", "c"]) == "High"
    assert risk_level(49, []) == "High"


def test_analyze_products_uses_nsfs_weighted_formula() -> None:
    products = [
        ProductOut(
            asin=f"B000000{i:02d}",
            title=f"Test Product {i}",
            brand=f"Brand {i % 5}",
            price=29.99,
            rating=4.4,
            review_count=120 + i,
            monthly_sales_est=250,
            is_sponsored=i <= 4,
        )
        for i in range(1, 21)
    ]

    result = analyze_products(
        keyword="sink organizer",
        products=products,
        budget_rmb=100000,
        target_price_min=20,
        target_price_max=40,
    )

    expected_nsfs = round(
        result["demand_score"] * 0.25
        + result["competition_score"] * 0.30
        + result["profit_score"] * 0.25
        + result["opportunity_score"] * 0.20,
        1,
    )
    assert result["nsfs_score"] == expected_nsfs
    assert result["score_details"].avg_reviews_top10 == 125.5
    assert result["score_details"].sponsored_density == 0.2

