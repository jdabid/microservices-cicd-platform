"""
Integration tests for auth feature (US-16)
Tests registration, login, and protected routes via TestClient.
"""


def _register_payload(**overrides) -> dict:
    data = {
        "email": "testuser@example.com",
        "password": "TestPass123",
        "full_name": "Test User",
    }
    data.update(overrides)
    return data


class TestRegister:
    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", json=_register_payload())

        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "testuser@example.com"
        assert body["full_name"] == "Test User"
        assert body["is_active"] is True
        assert "id" in body

    def test_register_duplicate_email(self, client):
        client.post("/api/v1/auth/register", json=_register_payload())
        response = client.post("/api/v1/auth/register", json=_register_payload())

        assert response.status_code == 409

    def test_register_weak_password(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json=_register_payload(password="weak"),
        )

        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        client.post("/api/v1/auth/register", json=_register_payload())

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "TestPass123"},
        )

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        client.post("/api/v1/auth/register", json=_register_payload())

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "WrongPass123"},
        )

        assert response.status_code == 401


class TestMe:
    def test_get_me_authenticated(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "auth@example.com"
        assert body["full_name"] == "Auth User"

    def test_get_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")

        assert response.status_code in (401, 403)
