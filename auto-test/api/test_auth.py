"""API tests for auth endpoints."""
import uuid

import pytest
import httpx


def test_health(client: httpx.Client) -> None:
    """GET /health returns ok."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"


def test_register(client: httpx.Client) -> None:
    """POST /api/auth/register creates user and returns token."""
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "full_name": "Test User",
        "password": "Test123!",
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "user" in data
    assert data["user"]["email"] == email
    assert "id" in data["user"]
    assert isinstance(data["user"]["id"], str)
    assert "token" in data
    assert "access_token" in data["token"]


def test_register_duplicate_email(client: httpx.Client) -> None:
    """POST /api/auth/register with existing email returns 400."""
    email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "full_name": "User", "password": "Test123!"}
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 200
    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400


def test_login(client: httpx.Client, base_url: str) -> None:
    """POST /api/auth/login with valid creds returns token."""
    # Use admin from reset-admin (admin@example.com / Admin123!)
    payload = {"email": "admin@example.com", "password": "Admin123!"}
    r = client.post("/api/auth/login", json=payload)
    if r.status_code != 200:
        pytest.skip("Admin user not found - run ./reset-admin.sh first")
    data = r.json()
    assert "user" in data
    assert "token" in data
    assert "access_token" in data["token"]


def test_login_invalid(client: httpx.Client) -> None:
    """POST /api/auth/login with invalid creds returns 401."""
    payload = {"email": "nonexistent@example.com", "password": "wrong"}
    r = client.post("/api/auth/login", json=payload)
    assert r.status_code == 401


def test_users_me(client: httpx.Client) -> None:
    """GET /api/users/me requires Bearer token."""
    r = client.get("/api/users/me")
    assert r.status_code == 401


def test_users_me_with_token(client: httpx.Client) -> None:
    """GET /api/users/me with valid token returns user."""
    login_payload = {"email": "admin@example.com", "password": "Admin123!"}
    login_r = client.post("/api/auth/login", json=login_payload)
    if login_r.status_code != 200:
        pytest.skip("Admin user not found - run ./reset-admin.sh first")
    token = login_r.json()["token"]["access_token"]
    r = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("email") == "admin@example.com"


def test_logout_with_token(client: httpx.Client) -> None:
    """POST /api/auth/logout with token returns success."""
    login_payload = {"email": "admin@example.com", "password": "Admin123!"}
    login_r = client.post("/api/auth/login", json=login_payload)
    if login_r.status_code != 200:
        pytest.skip("Admin user not found - run ./reset-admin.sh first")
    token = login_r.json()["token"]["access_token"]
    r = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json().get("message") == "Logged out successfully"
