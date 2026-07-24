"""API integration tests for auth + organizations against PostgreSQL."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from wealthos.core.database import SessionLocal, engine
from wealthos.main import app

AUTH = "/api/v1/auth"
ME = "/api/v1/me"
ORG_PATH = "/api/v1/organizations"


@pytest.fixture()
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _cleanup_tables() -> Generator[None]:
    yield
    with SessionLocal() as session:
        session.execute(text("DELETE FROM categories"))
        session.execute(text("DELETE FROM organization_memberships"))
        session.execute(text("DELETE FROM organizations"))
        session.execute(text("DELETE FROM users"))
        session.commit()


def _register(
    client: TestClient,
    *,
    email: str | None = None,
    organization_name: str = "Ricardo Personal",
) -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": email or f"user-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Ricardo Balam",
            "organization_name": organization_name,
            "currency": "MXN",
            "timezone": "America/Cancun",
            "locale": "es-MX",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_returns_201_and_token(client: TestClient) -> None:
    body = _register(client)
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["expires_in"] == 900


def test_login_returns_token(client: TestClient) -> None:
    email = f"login-{uuid4().hex[:8]}@example.com"
    _register(client, email=email)
    response = client.post(
        f"{AUTH}/login",
        data={"username": email, "password": "WealthOS-2026-Segura"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_me_requires_token(client: TestClient) -> None:
    assert client.get(f"{AUTH}/me").status_code == 401


def test_me_with_token_returns_user(client: TestClient) -> None:
    email = f"me-{uuid4().hex[:8]}@example.com"
    token = _register(client, email=email)["access_token"]
    response = client.get(f"{AUTH}/me", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_me_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(f"{AUTH}/me", headers=_auth_header("not-a-token"))
    assert response.status_code == 401


def test_me_organizations_only_returns_own(client: TestClient) -> None:
    token_a = _register(client, email=f"a-{uuid4().hex[:8]}@example.com")["access_token"]
    token_b = _register(
        client,
        email=f"b-{uuid4().hex[:8]}@example.com",
        organization_name="Other Org",
    )["access_token"]

    orgs_a = client.get(f"{ME}/organizations", headers=_auth_header(token_a)).json()
    orgs_b = client.get(f"{ME}/organizations", headers=_auth_header(token_b)).json()

    assert orgs_a["total"] == 1
    assert orgs_b["total"] == 1
    assert orgs_a["items"][0]["role"] == "owner"
    assert orgs_a["items"][0]["id"] != orgs_b["items"][0]["id"]


def test_member_endpoints_require_membership(client: TestClient) -> None:
    token_a = _register(client, email=f"a-{uuid4().hex[:8]}@example.com")["access_token"]
    token_b = _register(
        client,
        email=f"b-{uuid4().hex[:8]}@example.com",
        organization_name="B Org",
    )["access_token"]
    org_b = client.get(f"{ME}/organizations", headers=_auth_header(token_b)).json()["items"][0]

    response = client.get(
        f"{ORG_PATH}/{org_b['id']}/members",
        headers=_auth_header(token_a),
    )
    assert response.status_code == 404


def test_owner_can_list_members(client: TestClient) -> None:
    token = _register(client)["access_token"]
    org = client.get(f"{ME}/organizations", headers=_auth_header(token)).json()["items"][0]
    response = client.get(
        f"{ORG_PATH}/{org['id']}/members",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["role"] == "owner"


def test_postgres_engine_is_reachable() -> None:
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
