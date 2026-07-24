"""Concurrent debt payment integration test."""

from __future__ import annotations

from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
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
        session.execute(text("DELETE FROM cash_plan_item_matches"))
        session.execute(text("DELETE FROM cash_plan_items"))
        session.execute(text("DELETE FROM cash_plan_accounts"))
        session.execute(text("DELETE FROM cash_plans"))
        session.execute(text("DELETE FROM budget_allocation_matches"))
        session.execute(text("DELETE FROM budget_allocations"))
        session.execute(text("DELETE FROM budgets"))
        session.execute(text("DELETE FROM debt_payments"))
        session.execute(text("DELETE FROM debts"))
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


def test_concurrent_debt_payments_one_succeeds_one_fails(client: TestClient) -> None:
    register = client.post(
        f"{AUTH}/register",
        json={
            "email": f"dc-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Concurrent Debts",
            "organization_name": "Concurrent Debts Org",
        },
    )
    assert register.status_code == 201
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]

    bank = client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "Banco",
            "account_type": "checking",
            "currency": "MXN",
            "opening_balance": "50000.00",
        },
    ).json()
    card = client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "Tarjeta",
            "account_type": "credit_card",
            "currency": "MXN",
            "opening_balance": "-10000.00",
        },
    ).json()
    debt = client.post(
        f"{ORG}/{org_id}/debts",
        headers=headers,
        json={
            "account_id": card["id"],
            "name": "Tarjeta concurrente",
            "debt_type": "credit_card",
            "annual_interest_rate": "36.00",
            "minimum_payment": "500.00",
        },
    ).json()

    payloads = [
        {
            "source_account_id": bank["id"],
            "amount": "6000.00",
            "occurred_at": "2026-07-24T18:30:00Z",
            "description": "Pago A",
        },
        {
            "source_account_id": bank["id"],
            "amount": "6000.00",
            "occurred_at": "2026-07-24T18:31:00Z",
            "description": "Pago B",
        },
    ]

    def post_payment(payload: dict) -> int:
        with TestClient(app) as thread_client:
            response = thread_client.post(
                f"{ORG}/{org_id}/debts/{debt['id']}/payments",
                headers=headers,
                json=payload,
            )
            return response.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = sorted(executor.map(post_payment, payloads))

    assert statuses == [201, 400]

    card_after = client.get(f"{ORG}/{org_id}/accounts/{card['id']}", headers=headers).json()
    assert Decimal(str(card_after["current_balance"])) == Decimal("-4000.00")

    debt_after = client.get(f"{ORG}/{org_id}/debts/{debt['id']}", headers=headers).json()
    assert Decimal(str(debt_after["current_balance"])) == Decimal("4000.00")
    assert debt_after["status"] == "active"

    payments = client.get(
        f"{ORG}/{org_id}/debts/{debt['id']}/payments",
        headers=headers,
    ).json()
    assert payments["total"] == 1
