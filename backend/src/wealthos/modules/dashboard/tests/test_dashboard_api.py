"""Dashboard API integration tests (summary acceptance flow)."""

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


def _register(client: TestClient, org_name: str = "Dash Org") -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"d-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Dash",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    return {"headers": headers, "org_id": org_id}


def _category(client: TestClient, user: dict, *, type_: str, name: str) -> str:
    items = client.get(
        f"{ORG}/{user['org_id']}/categories",
        headers=user["headers"],
        params={"type": type_},
    ).json()["items"]
    match = next(item for item in items if item["name"] == name)
    return match["id"]


def test_dashboard_requires_auth(client: TestClient) -> None:
    assert client.get(f"{ORG}/{uuid4()}/dashboard/summary").status_code == 401


def test_dashboard_acceptance_flow(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    income_cat = _category(client, user, type_="income", name="Honorarios")
    vivienda = _category(client, user, type_="expense", name="Vivienda")
    alimentacion = _category(client, user, type_="expense", name="Alimentación")

    hsbc = client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "HSBC",
            "account_type": "checking",
            "currency": "MXN",
            "opening_balance": "20000.00",
        },
    ).json()
    gbm = client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "GBM",
            "account_type": "investment",
            "currency": "MXN",
            "opening_balance": "0.00",
        },
    ).json()
    card = client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "Tarjeta",
            "account_type": "credit_card",
            "currency": "MXN",
            "opening_balance": "-5000.00",
        },
    ).json()

    client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "income",
            "account_id": hsbc["id"],
            "category_id": income_cat,
            "amount": "10000.00",
            "description": "Ingreso",
            "occurred_at": "2026-07-10T12:00:00Z",
        },
    )
    client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "expense",
            "account_id": hsbc["id"],
            "category_id": vivienda,
            "amount": "3000.00",
            "description": "Renta",
            "occurred_at": "2026-07-11T12:00:00Z",
        },
    )
    client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "expense",
            "account_id": hsbc["id"],
            "category_id": alimentacion,
            "amount": "1000.00",
            "description": "Comida",
            "occurred_at": "2026-07-12T12:00:00Z",
        },
    )
    client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "transfer",
            "source_account_id": hsbc["id"],
            "destination_account_id": gbm["id"],
            "amount": "5000.00",
            "description": "A GBM",
            "occurred_at": "2026-07-13T12:00:00Z",
        },
    )
    voidable = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "expense",
            "account_id": hsbc["id"],
            "category_id": alimentacion,
            "amount": "2000.00",
            "description": "Anulable",
            "occurred_at": "2026-07-14T12:00:00Z",
        },
    ).json()
    client.post(
        f"{ORG}/{org_id}/transactions/{voidable['id']}/void",
        headers=headers,
    )

    hsbc_bal = client.get(f"{ORG}/{org_id}/accounts/{hsbc['id']}", headers=headers).json()
    gbm_bal = client.get(f"{ORG}/{org_id}/accounts/{gbm['id']}", headers=headers).json()
    card_bal = client.get(f"{ORG}/{org_id}/accounts/{card['id']}", headers=headers).json()
    assert Decimal(str(hsbc_bal["current_balance"])) == Decimal("21000.00")
    assert Decimal(str(gbm_bal["current_balance"])) == Decimal("5000.00")
    assert Decimal(str(card_bal["current_balance"])) == Decimal("-5000.00")

    summary = client.get(
        f"{ORG}/{org_id}/dashboard/summary",
        headers=headers,
        params={"period": "custom", "date_from": "2026-07-01", "date_to": "2026-07-31"},
    )
    assert summary.status_code == 200, summary.text
    body = summary.json()
    mxn_balance = body["balances"][0]
    assert mxn_balance["currency"] == "MXN"
    assert Decimal(str(mxn_balance["total_assets"])) == Decimal("26000.00")
    assert Decimal(str(mxn_balance["total_liabilities"])) == Decimal("5000.00")
    assert Decimal(str(mxn_balance["net_worth"])) == Decimal("21000.00")
    mxn_flow = body["cash_flow"][0]
    assert Decimal(str(mxn_flow["income"])) == Decimal("10000.00")
    assert Decimal(str(mxn_flow["expenses"])) == Decimal("4000.00")
    assert Decimal(str(mxn_flow["net_cash_flow"])) == Decimal("6000.00")
    assert body["goals"] == {"active": 0, "completed": 0}

    spending = client.get(
        f"{ORG}/{org_id}/dashboard/spending-by-category",
        headers=headers,
        params={"period": "custom", "date_from": "2026-07-01", "date_to": "2026-07-31"},
    )
    assert spending.status_code == 200, spending.text
    items = {item["category_name"]: item for item in spending.json()["series"][0]["items"]}
    assert Decimal(str(items["Vivienda"]["amount"])) == Decimal("3000.00")
    assert Decimal(str(items["Alimentación"]["amount"])) == Decimal("1000.00")

    cash_flow = client.get(
        f"{ORG}/{org_id}/dashboard/cash-flow",
        headers=headers,
        params={
            "period": "custom",
            "date_from": "2026-07-01",
            "date_to": "2026-07-03",
            "granularity": "day",
        },
    )
    assert cash_flow.status_code == 200
    assert len(cash_flow.json()["series"][0]["items"]) == 3

    accounts = client.get(f"{ORG}/{org_id}/dashboard/accounts", headers=headers)
    assert accounts.status_code == 200
    assert len(accounts.json()["groups"][0]["accounts"]) == 3

    recent = client.get(
        f"{ORG}/{org_id}/dashboard/recent-transactions",
        headers=headers,
        params={"limit": 5},
    )
    assert recent.status_code == 200
    assert recent.json()["total"] == 5


def test_dashboard_isolation_and_validation(client: TestClient) -> None:
    owner = _register(client, org_name="Owner Dash")
    stranger = _register(client, org_name="Stranger Dash")
    assert (
        client.get(
            f"{ORG}/{owner['org_id']}/dashboard/summary",
            headers=stranger["headers"],
        ).status_code
        == 404
    )
    invalid = client.get(
        f"{ORG}/{owner['org_id']}/dashboard/summary",
        headers=owner["headers"],
        params={"period": "this_month", "date_from": "2026-07-01"},
    )
    assert invalid.status_code == 422
    custom_missing = client.get(
        f"{ORG}/{owner['org_id']}/dashboard/summary",
        headers=owner["headers"],
        params={"period": "custom"},
    )
    assert custom_missing.status_code == 422
