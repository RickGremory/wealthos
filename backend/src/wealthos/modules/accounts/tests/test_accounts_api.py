"""API integration tests for accounts (auth + tenant isolation)."""

from __future__ import annotations

from collections.abc import Generator
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from wealthos.core.database import SessionLocal
from wealthos.main import app

AUTH = "/api/v1/auth"
ME = "/api/v1/me"
ORG = "/api/v1/organizations"


@pytest.fixture()
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _cleanup() -> Generator[None]:
    yield
    with SessionLocal() as session:
        session.execute(text("DELETE FROM transaction_entries"))
        session.execute(text("DELETE FROM transactions"))
        session.execute(text("DELETE FROM categories"))
        session.execute(text("DELETE FROM accounts"))
        session.execute(text("DELETE FROM organization_memberships"))
        session.execute(text("DELETE FROM organizations"))
        session.execute(text("DELETE FROM users"))
        session.commit()


def _register(client: TestClient, email: str | None = None, org_name: str = "Org") -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": email or f"u-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "User",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    me = client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {token}"}).json()
    orgs = client.get(f"{ME}/organizations", headers={"Authorization": f"Bearer {token}"}).json()
    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": me["id"],
        "org_id": orgs["items"][0]["id"],
    }


def test_accounts_require_auth(client: TestClient) -> None:
    assert client.get(f"{ORG}/{uuid4()}/accounts").status_code == 401


def test_account_lifecycle_and_isolation(client: TestClient) -> None:
    user_a = _register(client, org_name="Org A")
    user_b = _register(client, org_name="Org B")

    create = client.post(
        f"{ORG}/{user_a['org_id']}/accounts",
        headers=user_a["headers"],
        json={
            "name": "HSBC Nómina",
            "account_type": "checking",
            "currency": "MXN",
            "opening_balance": "15000.00",
            "institution_name": "HSBC",
            "last_four": "1234",
        },
    )
    assert create.status_code == 201, create.text
    account = create.json()
    assert account["classification"] == "asset"
    assert Decimal(str(account["current_balance"])) == Decimal("15000")

    client.post(
        f"{ORG}/{user_a['org_id']}/accounts",
        headers=user_a["headers"],
        json={"name": "GBM", "account_type": "investment", "currency": "MXN"},
    )
    client.post(
        f"{ORG}/{user_a['org_id']}/accounts",
        headers=user_a["headers"],
        json={
            "name": "HSBC Zero",
            "account_type": "credit_card",
            "currency": "MXN",
            "opening_balance": "-3400.50",
        },
    )

    listed = client.get(
        f"{ORG}/{user_a['org_id']}/accounts",
        headers=user_a["headers"],
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 3

    # Tenant isolation: B cannot see A's org accounts
    assert (
        client.get(
            f"{ORG}/{user_a['org_id']}/accounts",
            headers=user_b["headers"],
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"{ORG}/{user_a['org_id']}/accounts/{account['id']}",
            headers=user_b["headers"],
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"{ORG}/{user_b['org_id']}/accounts/{account['id']}",
            headers=user_b["headers"],
        ).status_code
        == 404
    )

    patched = client.patch(
        f"{ORG}/{user_a['org_id']}/accounts/{account['id']}",
        headers=user_a["headers"],
        json={"name": "HSBC Payroll"},
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "HSBC Payroll"

    archived = client.post(
        f"{ORG}/{user_a['org_id']}/accounts/{account['id']}/archive",
        headers=user_a["headers"],
    )
    assert archived.status_code == 200
    assert archived.json()["is_active"] is False

    active = client.get(
        f"{ORG}/{user_a['org_id']}/accounts",
        headers=user_a["headers"],
    ).json()
    assert all(item["id"] != account["id"] for item in active["items"])

    with_archived = client.get(
        f"{ORG}/{user_a['org_id']}/accounts",
        headers=user_a["headers"],
        params={"include_archived": True},
    ).json()
    assert any(item["id"] == account["id"] for item in with_archived["items"])


def test_viewer_cannot_create_account(client: TestClient) -> None:
    owner = _register(client, org_name="Owner Org")
    viewer = _register(client, org_name="Viewer Personal")

    add = client.post(
        f"{ORG}/{owner['org_id']}/members",
        headers=owner["headers"],
        json={"user_id": viewer["user_id"], "role": "viewer"},
    )
    assert add.status_code == 201, add.text

    denied = client.post(
        f"{ORG}/{owner['org_id']}/accounts",
        headers=viewer["headers"],
        json={"name": "Cash", "account_type": "cash", "currency": "MXN"},
    )
    assert denied.status_code == 403

    allowed_read = client.get(
        f"{ORG}/{owner['org_id']}/accounts",
        headers=viewer["headers"],
    )
    assert allowed_read.status_code == 200
