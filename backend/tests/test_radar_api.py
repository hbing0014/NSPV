from sqlalchemy.orm import Session

from app.models.tables import Category, ProductOpportunity


def create_opportunity(
    db_session: Session,
    *,
    category: Category,
    asin: str,
    product_name: str,
    npfs_score: float,
    risk_level: str = "low",
    avg_price: float = 29.99,
    profit_score: float = 80,
    launch_score: float = 82,
    estimated_budget_rmb: float = 30000,
) -> ProductOpportunity:
    opportunity = ProductOpportunity(
        category_id=category.id,
        asin=asin,
        product_name=product_name,
        brand="Seed",
        primary_keyword=product_name.lower(),
        avg_price=avg_price,
        avg_rating=4.4,
        avg_reviews_top10=420,
        min_reviews_top10=88,
        monthly_search_volume=18000,
        estimated_monthly_sales=900,
        estimated_monthly_revenue=26991,
        demand_score=80,
        competition_score=75,
        profit_score=profit_score,
        opportunity_score=78,
        launch_score=launch_score,
        supplier_score=76,
        npfs_score=npfs_score,
        estimated_budget_rmb=estimated_budget_rmb,
        estimated_moq=300,
        estimated_first_order_qty=300,
        estimated_launch_days=45,
        risk_level=risk_level,
        recommendation="worth_research",
        is_red_ocean=False,
        is_amazon_basics=False,
        is_fragile=False,
        is_seasonal=False,
        is_heavy=False,
        is_patent_risk=False,
        differentiation_paths=["Low review"],
        key_risks=[],
        key_opportunities=["Easy launch"],
    )
    db_session.add(opportunity)
    db_session.flush()
    return opportunity


def seed_radar_products(db_session: Session) -> list[ProductOpportunity]:
    kitchen = Category(category_name="Kitchen & Dining", marketplace="US", is_active=True, priority_level="high")
    home = Category(category_name="Home & Kitchen", marketplace="US", is_active=True, priority_level="high")
    db_session.add_all([kitchen, home])
    db_session.flush()
    products = [
        create_opportunity(
            db_session,
            category=kitchen,
            asin="RADAR00001",
            product_name="Under Sink Organizer",
            npfs_score=88,
            risk_level="low",
            avg_price=29.99,
            profit_score=82,
            launch_score=91,
            estimated_budget_rmb=28000,
        ),
        create_opportunity(
            db_session,
            category=kitchen,
            asin="RADAR00002",
            product_name="Spice Rack",
            npfs_score=79,
            risk_level="medium",
            avg_price=34.99,
            profit_score=91,
            launch_score=70,
            estimated_budget_rmb=24000,
        ),
        create_opportunity(
            db_session,
            category=home,
            asin="RADAR00003",
            product_name="Weighted Blanket",
            npfs_score=72,
            risk_level="high",
            avg_price=69.99,
            profit_score=70,
            launch_score=55,
            estimated_budget_rmb=48000,
        ),
    ]
    db_session.commit()
    return products


def test_radar_products_returns_default_top_opportunities(client, db_session: Session) -> None:
    seed_radar_products(db_session)

    response = client.get("/api/radar/products")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert [product["asin"] for product in data["products"]] == ["RADAR00001", "RADAR00002", "RADAR00003"]
    assert data["products"][0]["category"] == "Kitchen & Dining"


def test_radar_products_supports_filters(client, db_session: Session) -> None:
    seed_radar_products(db_session)

    response = client.get(
        "/api/radar/products",
        params={
            "category": "Kitchen & Dining",
            "risk_level": "low",
            "budget_max": 30000,
            "price_min": 20,
            "price_max": 40,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["products"][0]["asin"] == "RADAR00001"


def test_radar_products_supports_lowest_budget_sort(client, db_session: Session) -> None:
    seed_radar_products(db_session)

    response = client.get("/api/radar/products", params={"sort": "lowest_budget"})

    assert [product["asin"] for product in response.json()["products"]] == ["RADAR00002", "RADAR00001", "RADAR00003"]


def test_radar_products_supports_highest_profit_sort(client, db_session: Session) -> None:
    seed_radar_products(db_session)

    response = client.get("/api/radar/products", params={"sort": "highest_profit"})

    assert [product["asin"] for product in response.json()["products"]][:2] == ["RADAR00002", "RADAR00001"]


def test_radar_products_supports_easiest_launch_sort(client, db_session: Session) -> None:
    seed_radar_products(db_session)

    response = client.get("/api/radar/products", params={"sort": "easiest_launch"})

    assert [product["asin"] for product in response.json()["products"]][0] == "RADAR00001"


def test_radar_products_supports_lowest_risk_sort(client, db_session: Session) -> None:
    seed_radar_products(db_session)

    response = client.get("/api/radar/products", params={"sort": "lowest_risk"})

    assert [product["risk_level"] for product in response.json()["products"]] == ["low", "medium", "high"]


def test_radar_product_detail_returns_single_opportunity(client, db_session: Session) -> None:
    products = seed_radar_products(db_session)

    response = client.get(f"/api/radar/products/{products[0].id}")

    assert response.status_code == 200
    data = response.json()
    assert data["product_opportunity_id"] == products[0].id
    assert data["asin"] == "RADAR00001"
    assert data["key_opportunities"] == ["Easy launch"]


def test_radar_product_detail_returns_404_for_missing_opportunity(client) -> None:
    response = client.get("/api/radar/products/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PRODUCT_OPPORTUNITY_NOT_FOUND"


def test_discover_products_persists_category_for_radar_filter(client) -> None:
    response = client.post(
        "/api/discover/products",
        json={
            "category": "Kitchen & Dining",
            "marketplace": "US",
            "budget_rmb": 100000,
            "price_min": 20,
            "price_max": 40,
            "weight_limit_g": 500,
        },
    )
    assert response.status_code == 200

    radar_response = client.get("/api/radar/products", params={"category": "Kitchen & Dining"})

    assert radar_response.status_code == 200
    data = radar_response.json()
    assert data["total"] == response.json()["total_recommendations"]
    assert all(product["category"] == "Kitchen & Dining" for product in data["products"])
