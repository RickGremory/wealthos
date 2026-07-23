"""API integration tests for organizations + memberships against PostgreSQL."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from wealthos.core.database import SessionLocal, engine
from wealthos.main import app

ORG_PATH = "/api/v1/organizations"
USERS_PATH = "/api/v1/identity/users"


@pytest.fixture()
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _cleanup_tables() -> Generator[None]:
    yield
    with SessionLocal() as session:
        session.execute(text("DELETE FROM organization_memberships"))
        session.execute(text("DELETE FROM organizations"))
        session.execute(text("DELETE FROM users"))
        session.commit()


def _create_org(client: TestClient, slug: str | None = None) -> dict:
    response = client.post(
        ORG_PATH,
        json={
            "name": "Ricardo Personal",
            "slug": slug or f"org-{uuid4().hex[:8]}",
            "currency": "MXN",
            "timezone": "America/Cancun",
            "locale": "es-MX",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_user(client: TestClient, email: str | None = None) -> dict:
    response = client.post(
        USERS_PATH,
        json={
            "email": email or f"user-{uuid4().hex[:8]}@example.com",
            "display_name": "Ricardo Balam",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_post_organizations_returns_201_and_body(client: TestClient) -> None:
    slug = f"ricardo-personal-{uuid4().hex[:8]}"
    body = _create_org(client, slug=slug)
    assert body["slug"] == slug

    with SessionLocal() as session:
        row = session.execute(
            text("SELECT name, slug FROM organizations WHERE slug = :slug"),
            {"slug": slug},
        ).one()
    assert row.slug == slug


def test_post_organizations_rejects_duplicate_slug(client: TestClient) -> None:
    slug = f"shared-{uuid4().hex[:8]}"
    assert _create_org(client, slug=slug)
    response = client.post(
        ORG_PATH,
        json={
            "name": "Two",
            "slug": slug,
            "currency": "MXN",
            "timezone": "America/Cancun",
            "locale": "es-MX",
        },
    )
    assert response.status_code == 409


def test_post_organizations_rejects_invalid_slug_shape(client: TestClient) -> None:
    response = client.post(
        ORG_PATH,
        json={
            "name": "Bad",
            "slug": "Not Valid",
            "currency": "MXN",
            "timezone": "America/Cancun",
            "locale": "es-MX",
        },
    )
    assert response.status_code == 422


def test_membership_lifecycle_via_api(client: TestClient) -> None:
    org = _create_org(client)
    user = _create_user(client)

    add = client.post(
        f"{ORG_PATH}/{org['id']}/members",
        json={"user_id": user["id"], "role": "owner"},
    )
    assert add.status_code == 201
    membership = add.json()
    assert membership["role"] == "owner"
    assert membership["status"] == "active"
    assert membership["user_id"] == user["id"]

    listed = client.get(f"{ORG_PATH}/{org['id']}/members")
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["total"] == 1
    assert payload["items"][0]["email"] == user["email"]
    assert payload["items"][0]["display_name"] == "Ricardo Balam"
    assert payload["items"][0]["role"] == "owner"

    duplicate = client.post(
        f"{ORG_PATH}/{org['id']}/members",
        json={"user_id": user["id"], "role": "member"},
    )
    assert duplicate.status_code == 409


def test_add_member_missing_user_returns_404(client: TestClient) -> None:
    org = _create_org(client)
    response = client.post(
        f"{ORG_PATH}/{org['id']}/members",
        json={"user_id": str(uuid4()), "role": "member"},
    )
    assert response.status_code == 404


def test_add_member_missing_organization_returns_404(client: TestClient) -> None:
    user = _create_user(client)
    response = client.post(
        f"{ORG_PATH}/{uuid4()}/members",
        json={"user_id": user["id"], "role": "member"},
    )
    assert response.status_code == 404


def test_postgres_engine_is_reachable() -> None:
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
