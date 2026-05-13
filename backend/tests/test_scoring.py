import json
from pathlib import Path

import pytest

from app.schemas.analysis import ProductOut
from app.services.scoring import (
    SCORING_VERSION,
    analyze_products,
    demand_score,
    profit_score,
    recommendation,
    review_competition_score,
    risk_level,
    sponsored_score,
)


SCORING_FIXTURES_PATH = Path(__file__).parent / "fixtures" / "scoring_cases.json"


def load_scoring_fixtures() -> list[dict]:
    return json.loads(SCORING_FIXTURES_PATH.read_text(encoding="utf-8"))


def build_fixture_products(profile: dict) -> list[ProductOut]:
    products = []
    amazon_basics_rank = profile["amazon_basics_rank"]
    for rank in range(1, 21):
        brand = "Amazon Basics" if amazon_basics_rank == rank else f"Brand {rank % profile['brand_cycle']}"
        products.append(
            ProductOut(
                asin=f"BCASE{rank:05d}",
                title=f"Fixture Product {rank}",
                brand=brand,
                price=profile["price"],
                rating=profile["rating"],
                review_count=profile["review_start"] + (rank - 1) * profile["review_step"],
                monthly_sales_est=profile["monthly_sales_est"],
                is_sponsored=rank <= profile["sponsored_count"],
            )
        )
    return products


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
    assert result["scoring_version"] == SCORING_VERSION


@pytest.mark.parametrize("case", load_scoring_fixtures(), ids=lambda case: case["name"])
def test_scoring_fixtures_hold_recommendation_and_risk_level(case: dict) -> None:
    result = analyze_products(
        keyword=case["keyword"],
        products=build_fixture_products(case["profile"]),
        budget_rmb=case["budget_rmb"],
        target_price_min=case["target_price_min"],
        target_price_max=case["target_price_max"],
    )

    assert result["recommendation"] == case["expected_recommendation"]
    assert result["risk_level"] == case["expected_risk_level"]
