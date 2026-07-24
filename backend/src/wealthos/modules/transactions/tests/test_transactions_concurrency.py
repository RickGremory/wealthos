"""Concurrent balance update integration test."""

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


def test_concurrent_expenses_preserve_balance(client: TestClient) -> None:
    register = client.post(
        f"{AUTH}/register",
        json={
            "email": f"c-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Concurrent",
            "organization_name": "Concurrent Org",
        },
    )
    assert register.status_code == 201
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]

    account = client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "HSBC",
            "account_type": "checking",
            "currency": "MXN",
            "opening_balance": "10000.00",
        },
    ).json()
    expense_cat = client.get(
        f"{ORG}/{org_id}/categories",
        headers=headers,
        params={"type": "expense"},
    ).json()["items"][0]["id"]

    payloads = [
        {
            "transaction_type": "expense",
            "account_id": account["id"],
            "category_id": expense_cat,
            "amount": "1000.00",
            "description": "Gasto A",
            "occurred_at": "2026-07-24T18:30:00Z",
        },
        {
            "transaction_type": "expense",
            "account_id": account["id"],
            "category_id": expense_cat,
            "amount": "2000.00",
            "description": "Gasto B",
            "occurred_at": "2026-07-24T18:31:00Z",
        },
    ]

    def post_expense(payload: dict) -> int:
        with TestClient(app) as thread_client:
            response = thread_client.post(
                f"{ORG}/{org_id}/transactions",
                headers=headers,
                json=payload,
            )
            return response.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(post_expense, payloads))

    assert statuses == [201, 201]
    balance = client.get(
        f"{ORG}/{org_id}/accounts/{account['id']}",
        headers=headers,
    ).json()
    assert Decimal(str(balance["current_balance"])) == Decimal("7000.00")
