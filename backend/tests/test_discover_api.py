from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tables import DiscoveryReport, ProductOpportunity, Project


def discover_payload() -> dict:
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


def test_discover_products_returns_seed_opportunities(client, db_session: Session) -> None:
    response = client.post("/api/discover/products", json=discover_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["discovery_report_id"] > 0
    assert data["project_id"] > 0
    assert data["total_products_scanned"] == 10
    assert data["total_products_filtered"] > 0
    assert data["total_recommendations"] == len(data["products"])
    assert data["products"]

    first = data["products"][0]
    assert first["product_opportunity_id"] > 0
    assert first["category"] == "Kitchen & Dining"
    assert first["primary_keyword"]
    assert first["secondary_keywords"]
    assert first["long_tail_keywords"]
    assert first["npfs_score"] >= data["products"][-1]["npfs_score"]

    report = db_session.get(DiscoveryReport, data["discovery_report_id"])
    assert report is not None
    assert report.total_recommendations == len(data["products"])
    assert report.recommended_products == [product["product_opportunity_id"] for product in data["products"]]


def test_discover_products_saves_project_and_opportunities(client, db_session: Session) -> None:
    response = client.post("/api/discover/products", json=discover_payload())
    data = response.json()

    project = db_session.get(Project, data["project_id"])
    assert project is not None
    assert project.project_name == "Kitchen & Dining discovery"
    assert project.budget_rmb == 100000

    opportunities = db_session.scalars(select(ProductOpportunity).order_by(ProductOpportunity.npfs_score.desc())).all()
    assert len(opportunities) == data["total_recommendations"]
    assert [item.id for item in opportunities] == [product["product_opportunity_id"] for product in data["products"]]
    assert all(item.primary_keyword for item in opportunities)
    assert all(item.npfs_score > 0 for item in opportunities)


def test_discover_products_reuses_existing_project(client, db_session: Session) -> None:
    project = Project(
        project_name="Existing Discovery",
        category="Kitchen & Dining",
        budget_rmb=100000,
        marketplace="US",
        status="active",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    payload = discover_payload() | {"project_id": project.id}
    response = client.post("/api/discover/products", json=payload)

    assert response.status_code == 200
    assert response.json()["project_id"] == project.id
    assert db_session.query(Project).count() == 1


def test_discover_products_supports_strict_min_npfs_filter(client) -> None:
    response = client.post("/api/discover/products", json=discover_payload() | {"min_npfs": 99})

    assert response.status_code == 200
    data = response.json()
    assert data["total_recommendations"] == 0
    assert data["products"] == []


def test_discover_products_validates_price_range(client) -> None:
    response = client.post("/api/discover/products", json=discover_payload() | {"price_min": 40, "price_max": 20})

    assert response.status_code == 422
