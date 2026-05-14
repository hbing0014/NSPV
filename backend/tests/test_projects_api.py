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


def auth_headers(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "safe-password-123", "name": email.split("@")[0]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def analyze_payload(project_id: int | None = None) -> dict:
    payload = {
        "keyword": "sink organizer",
        "marketplace": "US",
        "category": "Kitchen & Dining",
        "budget_rmb": 100000,
        "target_price_min": 20,
        "target_price_max": 40,
        "exclude_red_ocean": True,
    }
    if project_id is not None:
        payload["project_id"] = project_id
    return payload


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

    response = client.post("/api/analyze", json=analyze_payload(project["id"]))

    assert response.status_code == 200
    assert response.json()["project_id"] == project["id"]


def test_analyze_rejects_missing_project(client: TestClient) -> None:
    response = client.post("/api/analyze", json=analyze_payload(999999))

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "PROJECT_NOT_FOUND"
    assert error["details"]["project_id"] == 999999


def test_authenticated_project_list_is_scoped_by_user(client: TestClient) -> None:
    user_a = auth_headers(client, "seller-a@example.com")
    user_b = auth_headers(client, "seller-b@example.com")

    project_a = client.post("/api/projects", json=project_payload(), headers=user_a).json()
    project_b = client.post(
        "/api/projects",
        json=project_payload() | {"project_name": "Storage Q2"},
        headers=user_b,
    ).json()

    user_a_projects = client.get("/api/projects", headers=user_a).json()
    user_b_projects = client.get("/api/projects", headers=user_b).json()
    anonymous_projects = client.get("/api/projects").json()

    assert [project["id"] for project in user_a_projects] == [project_a["id"]]
    assert [project["id"] for project in user_b_projects] == [project_b["id"]]
    assert anonymous_projects == []
    assert client.get(f"/api/projects/{project_a['id']}", headers=user_b).status_code == 404


def test_authenticated_reports_are_scoped_by_user(client: TestClient) -> None:
    user_a = auth_headers(client, "report-a@example.com")
    user_b = auth_headers(client, "report-b@example.com")
    project_a = client.post("/api/projects", json=project_payload(), headers=user_a).json()

    created = client.post("/api/analyze", json=analyze_payload(project_a["id"]), headers=user_a).json()

    assert created["project_id"] == project_a["id"]
    assert client.get("/api/reports", headers=user_a).json()[0]["report_id"] == created["report_id"]
    assert client.get("/api/reports", headers=user_b).json() == []
    assert client.get("/api/reports").json() == []
    assert client.get(f"/api/reports/{created['report_id']}", headers=user_b).status_code == 404
    assert client.get(f"/api/reports/{created['report_id']}").status_code == 404
    assert client.get(f"/api/reports/{created['report_id']}", headers=user_a).status_code == 200


def test_authenticated_user_cannot_analyze_into_other_user_project(client: TestClient) -> None:
    user_a = auth_headers(client, "owner@example.com")
    user_b = auth_headers(client, "intruder@example.com")
    project = client.post("/api/projects", json=project_payload(), headers=user_a).json()

    response = client.post("/api/analyze", json=analyze_payload(project["id"]), headers=user_b)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROJECT_NOT_FOUND"
