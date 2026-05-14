from fastapi.testclient import TestClient


def register_payload() -> dict:
    return {
        "email": "Seller@Example.com",
        "password": "safe-password-123",
        "name": "New Seller",
    }


def test_register_login_and_profile_flow(client: TestClient) -> None:
    register_response = client.post("/api/auth/register", json=register_payload())

    assert register_response.status_code == 200
    registered = register_response.json()
    assert registered["token_type"] == "bearer"
    assert registered["access_token"]
    assert registered["user"]["email"] == "seller@example.com"
    assert registered["user"]["name"] == "New Seller"
    assert "password_hash" not in registered["user"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": "seller@example.com", "password": "safe-password-123"},
    )

    assert login_response.status_code == 200
    logged_in = login_response.json()
    assert logged_in["access_token"]
    assert logged_in["user"]["id"] == registered["user"]["id"]

    profile_response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {logged_in['access_token']}"},
    )

    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["id"] == registered["user"]["id"]
    assert profile["email"] == "seller@example.com"


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    first_response = client.post("/api/auth/register", json=register_payload())
    assert first_response.status_code == 200

    duplicate_response = client.post("/api/auth/register", json=register_payload())

    assert duplicate_response.status_code == 400
    error = duplicate_response.json()["error"]
    assert error["code"] == "EMAIL_ALREADY_REGISTERED"


def test_login_rejects_invalid_password(client: TestClient) -> None:
    register_response = client.post("/api/auth/register", json=register_payload())
    assert register_response.status_code == 200

    response = client.post(
        "/api/auth/login",
        json={"email": "seller@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    error = response.json()["error"]
    assert error["code"] == "INVALID_CREDENTIALS"


def test_profile_requires_bearer_token(client: TestClient) -> None:
    response = client.get("/api/auth/profile")

    assert response.status_code == 401
    error = response.json()["error"]
    assert error["code"] == "UNAUTHORIZED"


def test_profile_rejects_invalid_token(client: TestClient) -> None:
    response = client.get("/api/auth/profile", headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401
    error = response.json()["error"]
    assert error["code"] == "UNAUTHORIZED"
