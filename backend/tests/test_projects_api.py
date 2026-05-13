from fastapi.testclient import TestClient


def project_payload() -> dict:
    return {
        "project_name": "Kitchen Q2",
        "category": "Kitchen & Dining",
        "budget_rmb": 100000,
        "marketplace": "US",
        "target_price_min": 20,
        "target_price_max": 40,
    }


def test_project_crud_flow(client: TestClient) -> None:
    created_response = client.post("/api/projects", json=project_payload())

    assert created_response.status_code == 200
    created = created_response.json()
    assert created["id"] > 0
    assert created["project_name"] == "Kitchen Q2"
    assert created["status"] == "active"
    assert created["target_price_min"] == 20
    assert created["target_price_max"] == 40

    list_response = client.get("/api/projects")
    assert list_response.status_code == 200
    assert [project["id"] for project in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/projects/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.put(
        f"/api/projects/{created['id']}",
        json={"project_name": "Kitchen Q3", "budget_rmb": 120000, "target_price_max": 45},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["project_name"] == "Kitchen Q3"
    assert updated["budget_rmb"] == 120000
    assert updated["target_price_max"] == 45

    delete_response = client.delete(f"/api/projects/{created['id']}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}

    missing_response = client.get(f"/api/projects/{created['id']}")
    assert missing_response.status_code == 404
    assert missing_response.json()["error"]["code"] == "PROJECT_NOT_FOUND"


def test_project_rejects_invalid_price_range(client: TestClient) -> None:
    payload = project_payload()
    payload["target_price_min"] = 50
    payload["target_price_max"] = 40

    response = client.post("/api/projects", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_analyze_can_use_existing_project(client: TestClient) -> None:
    project = client.post("/api/projects", json=project_payload()).json()
    payload = {
        "project_id": project["id"],
        "keyword": "sink organizer",
        "marketplace": "US",
        "category": "Kitchen & Dining",
        "budget_rmb": 100000,
        "target_price_min": 20,
        "target_price_max": 40,
        "exclude_red_ocean": True,
    }

    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 200
    assert response.json()["project_id"] == project["id"]


def test_analyze_rejects_missing_project(client: TestClient) -> None:
    payload = {
        "project_id": 999999,
        "keyword": "sink organizer",
        "marketplace": "US",
        "category": "Kitchen & Dining",
        "budget_rmb": 100000,
        "target_price_min": 20,
        "target_price_max": 40,
        "exclude_red_ocean": True,
    }

    response = client.post("/api/analyze", json=payload)

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "PROJECT_NOT_FOUND"
    assert error["details"]["project_id"] == 999999

