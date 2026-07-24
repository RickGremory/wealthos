"""API integration tests for transactions."""

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
        session.execute(text("DELETE FROM goal_manual_progress"))
        session.execute(text("DELETE FROM goal_accounts"))
        session.execute(text("DELETE FROM goals"))
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
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": me["id"],
        "org_id": orgs["items"][0]["id"],
    }


def _expense_category(client: TestClient, user: dict) -> str:
    cats = client.get(
        f"{ORG}/{user['org_id']}/categories",
        headers=user["headers"],
        params={"type": "expense"},
    ).json()["items"]
    return cats[0]["id"]


def _income_category(client: TestClient, user: dict) -> str:
    cats = client.get(
        f"{ORG}/{user['org_id']}/categories",
        headers=user["headers"],
        params={"type": "income"},
    ).json()["items"]
    return cats[0]["id"]


def _create_account(
    client: TestClient,
    user: dict,
    *,
    name: str,
    opening: str = "0.00",
    currency: str = "MXN",
) -> dict:
    response = client.post(
        f"{ORG}/{user['org_id']}/accounts",
        headers=user["headers"],
        json={
            "name": name,
            "account_type": "checking",
            "currency": currency,
            "opening_balance": opening,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_transactions_require_auth(client: TestClient) -> None:
    assert client.get(f"{ORG}/{uuid4()}/transactions").status_code == 401


def test_acceptance_flow_and_filters(client: TestClient) -> None:
    user = _register(client, org_name="Cashflow")
    org_id = user["org_id"]
    headers = user["headers"]
    income_cat = _income_category(client, user)
    expense_cat = _expense_category(client, user)

    hsbc = _create_account(client, user, name="HSBC", opening="20000.00")
    income = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "income",
            "account_id": hsbc["id"],
            "category_id": income_cat,
            "amount": "10000.00",
            "description": "Pago de cliente",
            "occurred_at": "2026-07-24T18:30:00Z",
        },
    )
    assert income.status_code == 201, income.text
    assert Decimal(str(income.json()["entries"][0]["amount"])) == Decimal("10000.00")

    refreshed = client.get(
        f"{ORG}/{org_id}/accounts/{hsbc['id']}",
        headers=headers,
    ).json()
    assert Decimal(str(refreshed["current_balance"])) == Decimal("30000.00")

    expense = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "expense",
            "account_id": hsbc["id"],
            "category_id": expense_cat,
            "amount": "1500.00",
            "description": "Supermercado",
            "occurred_at": "2026-07-24T19:00:00Z",
        },
    )
    assert expense.status_code == 201
    assert Decimal(str(expense.json()["entries"][0]["amount"])) == Decimal("-1500.00")

    gbm = _create_account(client, user, name="GBM", opening="0.00")
    transfer = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "transfer",
            "source_account_id": hsbc["id"],
            "destination_account_id": gbm["id"],
            "amount": "5000.00",
            "description": "Transferencia a GBM",
            "occurred_at": "2026-07-24T20:00:00Z",
        },
    )
    assert transfer.status_code == 201, transfer.text
    assert transfer.json()["source_account_id"] == hsbc["id"]
    assert transfer.json()["destination_account_id"] == gbm["id"]

    hsbc_bal = client.get(f"{ORG}/{org_id}/accounts/{hsbc['id']}", headers=headers).json()
    gbm_bal = client.get(f"{ORG}/{org_id}/accounts/{gbm['id']}", headers=headers).json()
    assert Decimal(str(hsbc_bal["current_balance"])) == Decimal("23500.00")
    assert Decimal(str(gbm_bal["current_balance"])) == Decimal("5000.00")

    voided = client.post(
        f"{ORG}/{org_id}/transactions/{expense.json()['id']}/void",
        headers=headers,
    )
    assert voided.status_code == 200
    assert voided.json()["status"] == "voided"
    hsbc_after = client.get(f"{ORG}/{org_id}/accounts/{hsbc['id']}", headers=headers).json()
    assert Decimal(str(hsbc_after["current_balance"])) == Decimal("25000.00")

    listed = client.get(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        params={"type": "expense", "limit": 10, "offset": 0},
    )
    assert listed.status_code == 200
    body = listed.json()
    assert body["limit"] == 10
    assert body["total"] >= 1

    patch = client.patch(
        f"{ORG}/{org_id}/transactions/{income.json()['id']}",
        headers=headers,
        json={"description": "Pago de cliente actualizado", "amount": "1"},
    )
    assert patch.status_code == 422


def test_roles_and_isolation(client: TestClient) -> None:
    owner = _register(client, org_name="Owner Org")
    viewer = _register(client, email=f"v-{uuid4().hex[:8]}@example.com", org_name="V Org")
    stranger = _register(client, email=f"s-{uuid4().hex[:8]}@example.com", org_name="S Org")

    add = client.post(
        f"{ORG}/{owner['org_id']}/members",
        headers=owner["headers"],
        json={"user_id": viewer["user_id"], "role": "viewer"},
    )
    assert add.status_code == 201

    assert (
        client.get(
            f"{ORG}/{owner['org_id']}/transactions",
            headers=viewer["headers"],
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"{ORG}/{owner['org_id']}/transactions",
            headers=stranger["headers"],
        ).status_code
        == 404
    )

    hsbc = _create_account(client, owner, name="Cash", opening="1000.00")
    income_cat = _income_category(client, owner)
    denied = client.post(
        f"{ORG}/{owner['org_id']}/transactions",
        headers=viewer["headers"],
        json={
            "transaction_type": "income",
            "account_id": hsbc["id"],
            "category_id": income_cat,
            "amount": "10.00",
            "description": "Blocked",
            "occurred_at": "2026-07-24T18:30:00Z",
        },
    )
    assert denied.status_code == 403

    created = client.post(
        f"{ORG}/{owner['org_id']}/transactions",
        headers=owner["headers"],
        json={
            "transaction_type": "income",
            "account_id": hsbc["id"],
            "category_id": income_cat,
            "amount": "10.00",
            "description": "Allowed",
            "occurred_at": "2026-07-24T18:30:00Z",
        },
    )
    assert created.status_code == 201

    cross = client.get(
        f"{ORG}/{stranger['org_id']}/transactions/{created.json()['id']}",
        headers=stranger["headers"],
    )
    assert cross.status_code == 404
