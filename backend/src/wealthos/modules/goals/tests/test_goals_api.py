"""Goals API integration tests (strategies + dashboard)."""

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
        session.execute(text("DELETE FROM tax_calculation_lines"))
        session.execute(text("DELETE FROM tax_calculations"))
        session.execute(text("DELETE FROM tax_payments"))
        session.execute(text("DELETE FROM tax_transaction_overrides"))
        session.execute(text("DELETE FROM tax_category_mappings"))
        session.execute(text("DELETE FROM tax_rule_categories"))
        session.execute(text("DELETE FROM tax_periods"))
        session.execute(text("DELETE FROM tax_rules"))
        session.execute(text("DELETE FROM tax_profiles"))
        session.execute(text("DELETE FROM goal_manual_progress"))
        session.execute(text("DELETE FROM goal_accounts"))
        session.execute(text("DELETE FROM goals"))
        session.execute(text("DELETE FROM transaction_entries"))
        session.execute(text("DELETE FROM transactions"))
        session.execute(text("DELETE FROM categories"))
        session.execute(text("DELETE FROM debt_payments"))
        session.execute(text("DELETE FROM debts"))
        session.execute(text("DELETE FROM accounts"))
        session.execute(text("DELETE FROM organization_memberships"))
        session.execute(text("DELETE FROM organizations"))
        session.execute(text("DELETE FROM users"))
        session.commit()


def _register(client: TestClient, org_name: str = "Goals Org") -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"g-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Goals",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    return {"headers": headers, "org_id": org_id}


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
    account_type: str = "savings",
) -> dict:
    response = client.post(
        f"{ORG}/{user['org_id']}/accounts",
        headers=user["headers"],
        json={
            "name": name,
            "account_type": account_type,
            "currency": currency,
            "opening_balance": opening,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_goals_require_auth(client: TestClient) -> None:
    assert client.get(f"{ORG}/{uuid4()}/goals").status_code == 401


def test_linked_accounts_progress_updates_with_deposits(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    income_cat = _income_category(client, user)
    savings = _create_account(client, user, name="Nu Ahorro", opening="42500.00")

    create = client.post(
        f"{ORG}/{org_id}/goals",
        headers=headers,
        json={
            "name": "Casa",
            "target_amount": "100000.00",
            "currency": "MXN",
            "strategy": "linked_accounts",
            "linked_account_ids": [savings["id"]],
        },
    )
    assert create.status_code == 201, create.text
    goal = create.json()
    assert Decimal(str(goal["current_amount"])) == Decimal("42500.00")
    assert Decimal(str(goal["completion_percentage"])) == Decimal("42.50")
    assert Decimal(str(goal["remaining_amount"])) == Decimal("57500.00")

    deposit = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "income",
            "account_id": savings["id"],
            "category_id": income_cat,
            "amount": "7500.00",
            "description": "Ahorro extra",
            "occurred_at": "2026-07-20T12:00:00Z",
        },
    )
    assert deposit.status_code == 201, deposit.text

    refreshed = client.get(f"{ORG}/{org_id}/goals/{goal['id']}", headers=headers)
    assert refreshed.status_code == 200
    body = refreshed.json()
    assert Decimal(str(body["current_amount"])) == Decimal("50000.00")
    assert Decimal(str(body["completion_percentage"])) == Decimal("50.00")


def test_manual_goal_ignores_account_changes(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    income_cat = _income_category(client, user)
    account = _create_account(client, user, name="HSBC", opening="10000.00")

    create = client.post(
        f"{ORG}/{org_id}/goals",
        headers=headers,
        json={
            "name": "Viaje Japón",
            "target_amount": "80000.00",
            "currency": "MXN",
            "strategy": "manual",
        },
    )
    assert create.status_code == 201, create.text
    goal_id = create.json()["id"]

    progress = client.post(
        f"{ORG}/{org_id}/goals/{goal_id}/manual-progress",
        headers=headers,
        json={"current_amount": "35000.00"},
    )
    assert progress.status_code == 200, progress.text
    assert Decimal(str(progress.json()["current_amount"])) == Decimal("35000.00")

    client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "income",
            "account_id": account["id"],
            "category_id": income_cat,
            "amount": "20000.00",
            "description": "No debe afectar goal manual",
            "occurred_at": "2026-07-21T12:00:00Z",
        },
    )
    after = client.get(f"{ORG}/{org_id}/goals/{goal_id}", headers=headers).json()
    assert Decimal(str(after["current_amount"])) == Decimal("35000.00")


def test_net_worth_goal_tracks_dashboard_net_worth(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    income_cat = _income_category(client, user)
    asset = _create_account(client, user, name="HSBC", opening="20000.00")
    client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "Card",
            "account_type": "credit_card",
            "currency": "MXN",
            "opening_balance": "-5000.00",
        },
    )

    create = client.post(
        f"{ORG}/{org_id}/goals",
        headers=headers,
        json={
            "name": "Independencia financiera",
            "target_amount": "100000.00",
            "currency": "MXN",
            "strategy": "net_worth_percentage",
        },
    )
    assert create.status_code == 201, create.text
    goal = create.json()
    # assets 20k - liability abs 5k = 15k
    assert Decimal(str(goal["current_amount"])) == Decimal("15000.00")
    assert Decimal(str(goal["completion_percentage"])) == Decimal("15.00")

    client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "income",
            "account_id": asset["id"],
            "category_id": income_cat,
            "amount": "10000.00",
            "description": "Bonus",
            "occurred_at": "2026-07-22T12:00:00Z",
        },
    )
    after = client.get(f"{ORG}/{org_id}/goals/{goal['id']}", headers=headers).json()
    assert Decimal(str(after["current_amount"])) == Decimal("25000.00")


def test_currency_mismatch_and_dashboard_summary(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    mxn = _create_account(client, user, name="Nu MXN", opening="1000.00")
    usd = _create_account(client, user, name="Wise USD", opening="100.00", currency="USD")

    mismatch = client.post(
        f"{ORG}/{org_id}/goals",
        headers=headers,
        json={
            "name": "Casa",
            "target_amount": "100000.00",
            "currency": "MXN",
            "strategy": "linked_accounts",
            "linked_account_ids": [usd["id"]],
        },
    )
    assert mismatch.status_code == 400

    linked = client.post(
        f"{ORG}/{org_id}/goals",
        headers=headers,
        json={
            "name": "Emergencia",
            "target_amount": "10000.00",
            "currency": "MXN",
            "strategy": "linked_accounts",
            "linked_account_ids": [mxn["id"]],
        },
    )
    assert linked.status_code == 201

    dash = client.get(f"{ORG}/{org_id}/dashboard/goals", headers=headers)
    assert dash.status_code == 200, dash.text
    body = dash.json()
    assert body["active_goals"] == 1
    assert body["completed_goals"] == 0
    assert Decimal(str(body["current_progress"])) == Decimal("1000.00")

    summary = client.get(f"{ORG}/{org_id}/dashboard/summary", headers=headers)
    assert summary.status_code == 200
    goals = summary.json()["goals"]
    assert goals["active"] == 1
    assert goals["completed"] == 0


def test_archive_goal(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    created = client.post(
        f"{ORG}/{org_id}/goals",
        headers=headers,
        json={
            "name": "Retiro",
            "target_amount": "1000000.00",
            "currency": "MXN",
            "strategy": "manual",
        },
    ).json()
    archived = client.post(
        f"{ORG}/{org_id}/goals/{created['id']}/archive",
        headers=headers,
    )
    assert archived.status_code == 200
    assert archived.json()["status"] == "archived"
    listed = client.get(f"{ORG}/{org_id}/goals", headers=headers).json()
    assert listed["total"] == 0
    with_archived = client.get(
        f"{ORG}/{org_id}/goals",
        headers=headers,
        params={"include_archived": True},
    ).json()
    assert with_archived["total"] == 1
