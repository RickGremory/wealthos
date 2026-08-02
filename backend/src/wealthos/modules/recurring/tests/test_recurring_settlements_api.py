"""API tests: confirm occurrence via Transaction + settlement link/void."""

from __future__ import annotations

from collections.abc import Generator
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
        session.execute(text("DELETE FROM planned_cash_flows"))
        session.execute(text("DELETE FROM planning_settings"))
        session.execute(text("DELETE FROM recurring_occurrence_settlements"))
        session.execute(text("DELETE FROM recurring_occurrence_exceptions"))
        session.execute(text("DELETE FROM recurring_rule_pauses"))
        session.execute(text("DELETE FROM recurring_rule_versions"))
        session.execute(text("DELETE FROM recurring_rules"))
        session.execute(text("DELETE FROM timeline_events"))
        session.execute(text("DELETE FROM debt_payments"))
        session.execute(text("DELETE FROM debts"))
        session.execute(text("DELETE FROM goal_manual_progress"))
        session.execute(text("DELETE FROM goal_accounts"))
        session.execute(text("DELETE FROM goals"))
        session.execute(text("DELETE FROM transaction_entries"))
        session.execute(text("DELETE FROM transactions"))
        session.execute(text("DELETE FROM categories"))
        session.execute(text("DELETE FROM accounts"))
        session.execute(text("DELETE FROM legal_consents"))
        session.execute(text("DELETE FROM organization_memberships"))
        session.execute(text("DELETE FROM organizations"))
        session.execute(text("DELETE FROM users"))
        session.commit()


def _register(client: TestClient) -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"s-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Settler",
            "organization_name": f"Settle {uuid4().hex[:6]}",
            "legal_acceptances": [
                {"document_type": "terms_of_service", "version": "1.0", "accepted": True},
                {"document_type": "privacy_notice", "version": "1.0", "acknowledged": True},
            ],
            "marketing_consent": False,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    return {"headers": headers, "org_id": org_id}


def test_confirm_via_transaction_then_void_restores(client: TestClient) -> None:
    user = _register(client)
    org = user["org_id"]
    headers = user["headers"]

    accounts = client.get(f"{ORG}/{org}/accounts", headers=headers)
    assert accounts.status_code == 200, accounts.text
    account_items = accounts.json()["items"]
    if account_items:
        account_id = account_items[0]["id"]
    else:
        created = client.post(
            f"{ORG}/{org}/accounts",
            headers=headers,
            json={
                "name": "Checking",
                "account_type": "checking",
                "currency": "MXN",
                "opening_balance": "5000.00",
            },
        )
        assert created.status_code == 201, created.text
        account_id = created.json()["id"]

    cats = client.get(
        f"{ORG}/{org}/categories",
        headers=headers,
        params={"type": "expense"},
    )
    assert cats.status_code == 200, cats.text
    assert cats.json()["items"], cats.text
    category_id = cats.json()["items"][0]["id"]

    rule = client.post(
        f"{ORG}/{org}/recurring",
        headers=headers,
        json={
            "name": "Internet",
            "direction": "outflow",
            "amount": "800.00",
            "currency": "MXN",
            "starts_on": "2026-07-15",
            "account_id": account_id,
            "category_id": category_id,
            "pattern": {
                "frequency": "monthly",
                "interval": 1,
                "day_of_month": 15,
                "end_of_month": False,
            },
        },
    )
    assert rule.status_code == 201, rule.text
    rule_id = rule.json()["id"]
    occurrence_key = f"recurring:{rule_id}:occurrence:2026-08-15"

    before = client.get(
        f"{ORG}/{org}/recurring/occurrences",
        headers=headers,
        params={"from": "2026-08-01", "to": "2026-08-31", "currency": "MXN"},
    )
    assert before.status_code == 200, before.text
    assert before.json()[0]["status"] in {"expected", "pending", "upcoming", "due"}

    txn = client.post(
        f"{ORG}/{org}/transactions",
        headers=headers,
        json={
            "transaction_type": "expense",
            "account_id": account_id,
            "category_id": category_id,
            "amount": "800.00",
            "description": "Internet agosto",
            "occurred_at": "2026-08-15T12:00:00Z",
            "source": {
                "type": "recurring_occurrence",
                "occurrence_key": occurrence_key,
                "related_resource_type": "recurring_rule",
                "related_resource_id": rule_id,
            },
        },
    )
    assert txn.status_code == 201, txn.text
    body = txn.json()
    assert body["source"]["occurrence_key"] == occurrence_key
    txn_id = body["id"]

    after = client.get(
        f"{ORG}/{org}/recurring/occurrences",
        headers=headers,
        params={"from": "2026-08-01", "to": "2026-08-31", "currency": "MXN"},
    )
    assert after.status_code == 200, after.text
    assert after.json()[0]["status"] in {"confirmed", "settled", "matched"}
    assert after.json()[0]["actual_amount"] is not None

    voided = client.post(
        f"{ORG}/{org}/transactions/{txn_id}/void",
        headers=headers,
    )
    assert voided.status_code == 200, voided.text
    assert voided.json()["status"] == "voided"

    restored = client.get(
        f"{ORG}/{org}/recurring/occurrences",
        headers=headers,
        params={"from": "2026-08-01", "to": "2026-08-31", "currency": "MXN"},
    )
    assert restored.status_code == 200, restored.text
    assert restored.json()[0]["status"] in {"expected", "pending", "upcoming", "due"}
