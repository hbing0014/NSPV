from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.tables import ScraperRun


def test_mock_scraper_provider_supports_analyze(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        json={
            "keyword": "sink organizer",
            "marketplace": "US",
            "category": "Kitchen & Dining",
            "budget_rmb": 100000,
            "target_price_min": 20,
            "target_price_max": 40,
            "exclude_red_ocean": True,
        },
    )

    assert response.status_code == 200
    assert len(response.json()["products"]) == 20


def test_unimplemented_scraper_provider_records_failed_run(client: TestClient, db_session: Session) -> None:
    settings = get_settings()
    original_provider = settings.scraper_provider
    settings.scraper_provider = "brightdata"

    try:
        response = client.post(
            "/api/analyze",
            json={
                "keyword": "sink organizer",
                "marketplace": "US",
                "category": "Kitchen & Dining",
                "budget_rmb": 100000,
                "target_price_min": 20,
                "target_price_max": 40,
                "exclude_red_ocean": True,
            },
        )
    finally:
        settings.scraper_provider = original_provider

    assert response.status_code == 503
    error = response.json()["error"]
    assert error["code"] == "SCRAPER_FAILED"
    assert "not implemented yet" in error["message"]

    scraper_run = db_session.scalars(select(ScraperRun)).one()
    assert scraper_run.provider == "brightdata"
    assert scraper_run.status == "failed"
    assert scraper_run.product_count == 0
    assert "not implemented yet" in (scraper_run.error_message or "")
    assert scraper_run.finished_at is not None
