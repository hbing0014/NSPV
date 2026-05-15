from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tables import Category, DiscoveryReport, ProductOpportunity, SelectionReport
from app.schemas.discovery import DiscoveryRequest
from app.services.discovery.discovery_service import discover_products


def default_discovery_payload() -> dict:
    return {
        "category": "Kitchen & Dining",
        "marketplace": "US",
        "budget_rmb": 100000,
        "risk_preference": "low",
        "price_min": 20,
        "price_max": 40,
        "weight_limit_g": 500,
        "exclude_red_ocean": True,
        "exclude_amazon_basics": True,
        "exclude_fragile": True,
        "exclude_seasonal": True,
    }


def test_v2_fixed_discovery_fixture_scores_are_stable() -> None:
    result = discover_products(DiscoveryRequest(**default_discovery_payload()))

    assert result.total_products_scanned == 10
    assert result.total_products_filtered == 7
    assert result.total_recommendations == 3

    stable_scores = [
        (
            product.source.asin,
            product.source.product_name,
            product.npfs_score,
            product.launch_score,
            product.supplier_score,
            product.risk_level,
            product.recommendation,
            product.estimated_budget_rmb,
            product.estimated_moq,
        )
        for product in result.products
    ]

    assert stable_scores == [
        ("NSPVK00001", "Under Sink Organizer", 85.8, 86.25, 86.75, "low", "strongly_recommended", 32692.18, 300),
        ("NSPVK00002", "Fridge Can Organizer", 84.1, 89.25, 86.75, "low", "worth_research", 27551.38, 300),
        ("NSPVK00008", "Magnetic Measuring Spoons", 81.12, 89.25, 75.75, "medium", "worth_research", 24743.38, 300),
    ]


def test_v2_discover_persists_contract_for_radar(client, db_session: Session) -> None:
    response = client.post("/api/discover/products", json=default_discovery_payload())

    assert response.status_code == 200
    data = response.json()
    opportunity_ids = [product["product_opportunity_id"] for product in data["products"]]

    category = db_session.scalar(select(Category).where(Category.category_name == "Kitchen & Dining"))
    assert category is not None
    assert category.marketplace == "US"
    assert category.priority_level == "high"

    report = db_session.get(DiscoveryReport, data["discovery_report_id"])
    assert report is not None
    assert report.recommended_products == opportunity_ids
    assert report.total_products_scanned == 10
    assert report.total_products_filtered == 7
    assert report.total_recommendations == 3

    opportunities = db_session.scalars(
        select(ProductOpportunity).where(ProductOpportunity.id.in_(opportunity_ids)).order_by(ProductOpportunity.npfs_score.desc())
    ).all()
    assert [opportunity.id for opportunity in opportunities] == opportunity_ids
    assert all(opportunity.category_id == category.id for opportunity in opportunities)
    assert all(opportunity.primary_keyword for opportunity in opportunities)
    assert all(opportunity.estimated_budget_rmb > 0 for opportunity in opportunities)


def test_v2_radar_detail_matches_discovered_product(client) -> None:
    discovered = client.post("/api/discover/products", json=default_discovery_payload()).json()
    first = discovered["products"][0]

    response = client.get(f"/api/radar/products/{first['product_opportunity_id']}")

    assert response.status_code == 200
    detail = response.json()
    assert detail["product_opportunity_id"] == first["product_opportunity_id"]
    assert detail["asin"] == first["asin"]
    assert detail["product_name"] == first["product_name"]
    assert detail["primary_keyword"] == first["primary_keyword"]
    assert detail["npfs_score"] == first["npfs_score"]
    assert detail["launch_score"] == first["launch_score"]
    assert detail["supplier_score"] == first["supplier_score"]
    assert detail["key_opportunities"] == first["key_opportunities"]


def test_v2_product_to_validate_keyword_linkage(client, db_session: Session) -> None:
    discovered = client.post("/api/discover/products", json=default_discovery_payload()).json()
    product = discovered["products"][0]

    response = client.post(
        "/api/analyze",
        json={
            "project_id": discovered["project_id"],
            "product_opportunity_id": product["product_opportunity_id"],
            "keyword": product["primary_keyword"],
            "marketplace": "US",
            "category": product["category"],
            "budget_rmb": 100000,
            "target_price_min": 20,
            "target_price_max": 40,
            "exclude_red_ocean": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == discovered["project_id"]
    assert data["input_payload"]["product_opportunity_id"] == product["product_opportunity_id"]
    assert data["keyword"] == product["primary_keyword"]
    assert data["analysis_status"] == "completed"

    report = db_session.get(SelectionReport, data["report_id"])
    assert report is not None
    assert report.product_opportunity_id == product["product_opportunity_id"]
    assert report.project_id == discovered["project_id"]
