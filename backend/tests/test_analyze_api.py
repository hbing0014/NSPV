from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.tables import ProductOpportunity, ScraperRun, SelectionReport
from app.services.scoring import SCORING_VERSION


def analyze_payload() -> dict:
    return {
        "keyword": "sink organizer",
        "marketplace": "US",
        "category": "Kitchen & Dining",
        "budget_rmb": 100000,
        "target_price_min": 20,
        "target_price_max": 40,
        "exclude_red_ocean": True,
    }


def test_analyze_creates_report(client: TestClient) -> None:
    response = client.post("/api/analyze", json=analyze_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] > 0
    assert data["project_id"] > 0
    assert data["scraper_run_id"] > 0
    assert data["keyword"] == "sink organizer"
    assert 0 <= data["nsfs_score"] <= 100
    assert data["recommendation"] in {"Strongly Recommended", "Worth Research", "Caution", "Avoid"}
    assert len(data["products"]) == 20
    assert data["input_payload"] == analyze_payload() | {"project_id": None, "product_opportunity_id": None, "locale": "zh-CN"}
    assert data["scoring_version"] == SCORING_VERSION
    assert data["analysis_status"] == "completed"
    assert data["error_message"] is None


def test_report_detail_returns_saved_snapshot(client: TestClient) -> None:
    created = client.post("/api/analyze", json=analyze_payload()).json()

    response = client.get(f"/api/reports/{created['report_id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == created["report_id"]
    assert data["scraper_run_id"] == created["scraper_run_id"]
    assert data["products"] == created["products"]
    assert data["input_payload"] == created["input_payload"]
    assert data["scoring_version"] == created["scoring_version"]
    assert data["analysis_status"] == "completed"


def test_analyze_records_successful_scraper_run(client: TestClient, db_session: Session) -> None:
    created = client.post("/api/analyze", json=analyze_payload()).json()

    scraper_run = db_session.get(ScraperRun, created["scraper_run_id"])

    assert scraper_run is not None
    assert scraper_run.keyword == "sink organizer"
    assert scraper_run.marketplace == "US"
    assert scraper_run.provider == "mock"
    assert scraper_run.status == "completed"
    assert scraper_run.product_count == 20
    assert scraper_run.error_message is None
    assert scraper_run.finished_at is not None


def test_analyze_rejects_invalid_price_range(client: TestClient) -> None:
    payload = analyze_payload()
    payload["target_price_min"] = 45
    payload["target_price_max"] = 20

    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["message"] == "target_price_min cannot exceed target_price_max"
    assert error["details"]["field"] == "target_price_min"


def test_report_not_found(client: TestClient) -> None:
    response = client.get("/api/reports/999999")

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "REPORT_NOT_FOUND"
    assert error["message"] == "Report not found"
    assert error["details"]["report_id"] == 999999


def test_request_validation_error_uses_error_contract(client: TestClient) -> None:
    payload = analyze_payload()
    payload["budget_rmb"] = 0

    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["message"] == "Request validation failed."
    assert error["details"]["errors"]


def test_analyze_defaults_to_chinese_locale(client: TestClient) -> None:
    response = client.post("/api/analyze", json=analyze_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["input_payload"]["locale"] == "zh-CN"
    assert "需求" in data["summary"]
    assert data["suggestions"][0] == "避免只围绕主关键词正面竞争"


def test_analyze_supports_english_locale(client: TestClient) -> None:
    payload = analyze_payload() | {"locale": "en"}
    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["input_payload"]["locale"] == "en"
    assert "Demand" in data["summary"]
    assert data["suggestions"][0] == "Avoid competing only on the main keyword."


def test_analyze_rejects_unsupported_locale(client: TestClient) -> None:
    payload = analyze_payload() | {"locale": "ja"}
    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"


def test_analyze_links_product_opportunity(client: TestClient, db_session: Session) -> None:
    opportunity = ProductOpportunity(
        asin="B000TEST01",
        product_name="Under Sink Organizer",
        primary_keyword="under sink organizer",
        avg_price=29.99,
        avg_rating=4.4,
        avg_reviews_top10=420,
        min_reviews_top10=88,
        monthly_search_volume=18000,
        estimated_monthly_sales=900,
        estimated_monthly_revenue=26991,
        demand_score=80,
        competition_score=75,
        profit_score=82,
        opportunity_score=88,
        launch_score=90,
        supplier_score=85,
        npfs_score=82,
        estimated_budget_rmb=30000,
        estimated_moq=300,
        estimated_first_order_qty=300,
        estimated_launch_days=45,
        risk_level="low",
        recommendation="worth_research",
        is_red_ocean=False,
        is_amazon_basics=False,
        is_fragile=False,
        is_seasonal=False,
        is_heavy=False,
        is_patent_risk=False,
    )
    db_session.add(opportunity)
    db_session.commit()
    db_session.refresh(opportunity)

    response = client.post("/api/analyze", json=analyze_payload() | {"product_opportunity_id": opportunity.id})

    assert response.status_code == 200
    report = response.json()
    assert report["input_payload"]["product_opportunity_id"] == opportunity.id
    saved_report = db_session.get(SelectionReport, report["report_id"])
    assert saved_report is not None
    assert saved_report.product_opportunity_id == opportunity.id


def test_analyze_rejects_missing_product_opportunity(client: TestClient) -> None:
    response = client.post("/api/analyze", json=analyze_payload() | {"product_opportunity_id": 999999})

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "PRODUCT_OPPORTUNITY_NOT_FOUND"
