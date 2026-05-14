from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.discovery import (
    DiscoveryRequest,
    LaunchScoreOut,
    ProductOpportunityOut,
)


def now() -> datetime:
    return datetime.now(timezone.utc)


def test_discovery_request_accepts_default_filters() -> None:
    request = DiscoveryRequest(
        category="Kitchen & Dining",
        budget_rmb=100000,
        price_min=20,
        price_max=40,
    )

    assert request.marketplace == "US"
    assert request.risk_preference == "balanced"
    assert request.exclude_red_ocean is True
    assert request.exclude_amazon_basics is True
    assert request.exclude_fragile is True
    assert request.exclude_seasonal is True


def test_discovery_request_rejects_invalid_price_range() -> None:
    with pytest.raises(ValidationError, match="price_min cannot exceed price_max"):
        DiscoveryRequest(
            category="Kitchen & Dining",
            budget_rmb=100000,
            price_min=40,
            price_max=20,
        )


def test_discovery_request_rejects_out_of_range_score_filters() -> None:
    with pytest.raises(ValidationError):
        DiscoveryRequest(
            category="Kitchen & Dining",
            budget_rmb=100000,
            min_launch_score=101,
        )


def test_launch_score_out_rejects_invalid_score() -> None:
    with pytest.raises(ValidationError):
        LaunchScoreOut(
            id=1,
            asin="B000TEST01",
            launch_score=120,
            created_at=now(),
            updated_at=now(),
        )


def test_product_opportunity_out_can_validate_orm_object() -> None:
    opportunity = SimpleNamespace(
        id=1,
        category_id=2,
        asin="B000TEST01",
        product_name="Under Sink Organizer",
        brand="StoragePro",
        primary_keyword="under sink organizer",
        keyword_cluster_id=None,
        avg_price=29.99,
        avg_rating=4.4,
        avg_reviews_top10=420,
        min_reviews_top10=88,
        monthly_search_volume=18000,
        estimated_monthly_sales=900,
        estimated_monthly_revenue=26991.0,
        demand_score=78,
        competition_score=82,
        profit_score=76,
        opportunity_score=84,
        launch_score=88,
        supplier_score=80,
        npfs_score=81.6,
        estimated_budget_rmb=38000,
        estimated_moq=300,
        estimated_first_order_qty=300,
        estimated_launch_days=45,
        risk_level="low",
        recommendation="strongly_recommended",
        is_red_ocean=False,
        is_amazon_basics=False,
        is_fragile=False,
        is_seasonal=False,
        is_heavy=False,
        is_patent_risk=False,
        differentiation_paths=["larger size", "easy clean design"],
        key_risks=["PPC may rise"],
        key_opportunities=["Low review barrier"],
        created_at=now(),
        updated_at=now(),
    )

    output = ProductOpportunityOut.model_validate(opportunity)

    assert output.asin == "B000TEST01"
    assert output.primary_keyword == "under sink organizer"
    assert output.npfs_score == 81.6
    assert output.differentiation_paths == ["larger size", "easy clean design"]
