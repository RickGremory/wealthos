"""API integration tests for POST /organizations (SQLite session override)."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from wealthos.core.database import Base, get_db
from wealthos.main import app

# Register models on Base.metadata before create_all.
from wealthos.modules.organizations.infrastructure.models import OrganizationModel  # noqa: F401


@pytest.fixture()
def client() -> Generator[TestClient]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db() -> Generator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_post_organizations_creates_workspace(client: TestClient) -> None:
    response = client.post(
        "/organizations",
        json={
            "name": "Ricardo Personal",
            "slug": "ricardo-personal",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ricardo Personal"
    assert body["slug"] == "ricardo-personal"
    assert body["currency"] == "MXN"
    assert body["timezone"] == "America/Mexico_City"
    assert body["locale"] == "es_MX"
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_post_organizations_rejects_duplicate_slug(client: TestClient) -> None:
    payload = {"name": "One", "slug": "shared-space"}
    assert client.post("/organizations", json=payload).status_code == 201

    response = client.post(
        "/organizations",
        json={"name": "Two", "slug": "shared-space"},
    )
    assert response.status_code == 409


def test_post_organizations_rejects_invalid_slug_shape(client: TestClient) -> None:
    response = client.post(
        "/organizations",
        json={"name": "Bad", "slug": "Not Valid"},
    )
    assert response.status_code == 422
