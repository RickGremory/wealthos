"""API integration tests for POST /api/v1/organizations against PostgreSQL."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from wealthos.core.database import SessionLocal, engine
from wealthos.main import app

API_PATH = "/api/v1/organizations"


@pytest.fixture()
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _cleanup_organizations() -> Generator[None]:
    """Keep the shared Postgres clean between API tests."""
    yield
    with SessionLocal() as session:
        session.execute(text("DELETE FROM organizations"))
        session.commit()


def test_post_organizations_returns_201_and_body(client: TestClient) -> None:
    slug = f"ricardo-personal-{uuid4().hex[:8]}"
    response = client.post(
        API_PATH,
        json={
            "name": "Ricardo Personal",
            "slug": slug,
            "currency": "MXN",
            "timezone": "America/Cancun",
            "locale": "es-MX",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ricardo Personal"
    assert body["slug"] == slug
    assert body["currency"] == "MXN"
    assert body["timezone"] == "America/Cancun"
    assert body["locale"] == "es-MX"
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]

    with SessionLocal() as session:
        row = session.execute(
            text("SELECT name, slug FROM organizations WHERE slug = :slug"),
            {"slug": slug},
        ).one()
    assert row.name == "Ricardo Personal"
    assert row.slug == slug


def test_post_organizations_rejects_duplicate_slug(client: TestClient) -> None:
    slug = f"shared-space-{uuid4().hex[:8]}"
    payload = {
        "name": "One",
        "slug": slug,
        "currency": "MXN",
        "timezone": "America/Cancun",
        "locale": "es-MX",
    }
    assert client.post(API_PATH, json=payload).status_code == 201

    response = client.post(
        API_PATH,
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
        API_PATH,
        json={
            "name": "Bad",
            "slug": "Not Valid",
            "currency": "MXN",
            "timezone": "America/Cancun",
            "locale": "es-MX",
        },
    )
    assert response.status_code == 422


def test_postgres_engine_is_reachable() -> None:
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
