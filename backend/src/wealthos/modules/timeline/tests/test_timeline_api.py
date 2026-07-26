"""Timeline API integration tests."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta
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
            "email": f"tl-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Timeline",
            "organization_name": "Timeline Org",
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


def _setup_accounts(client: TestClient, user: dict) -> dict:
    checking = client.post(
        f"{ORG}/{user['org_id']}/accounts",
        headers=user["headers"],
        json={
            "name": "Checking",
            "account_type": "checking",
            "currency": "MXN",
        },
    )
    assert checking.status_code == 201, checking.text
    liability = client.post(
        f"{ORG}/{user['org_id']}/accounts",
        headers=user["headers"],
        json={
            "name": "Card",
            "account_type": "credit_card",
            "currency": "MXN",
        },
    )
    assert liability.status_code == 201, liability.text
    cats = client.get(
        f"{ORG}/{user['org_id']}/categories",
        headers=user["headers"],
    ).json()["items"]
    income_cat = next(c["id"] for c in cats if c["category_type"] == "income")
    expense_cat = next(c["id"] for c in cats if c["category_type"] == "expense")
    return {
        "checking_id": checking.json()["id"],
        "liability_id": liability.json()["id"],
        "income_cat": income_cat,
        "expense_cat": expense_cat,
    }


def test_timeline_lists_significant_transaction_events(client: TestClient) -> None:
    user = _register(client)
    accounts = _setup_accounts(client, user)
    occurred = datetime.now(UTC).isoformat()

    income = client.post(
        f"{ORG}/{user['org_id']}/transactions",
        headers=user["headers"],
        json={
            "transaction_type": "income",
            "account_id": accounts["checking_id"],
            "category_id": accounts["income_cat"],
            "amount": "10000.00",
            "description": "Nomina",
            "occurred_at": occurred,
        },
    )
    assert income.status_code == 201, income.text

    micro = client.post(
        f"{ORG}/{user['org_id']}/transactions",
        headers=user["headers"],
        json={
            "transaction_type": "expense",
            "account_id": accounts["checking_id"],
            "category_id": accounts["expense_cat"],
            "amount": "10.00",
            "description": "Cafe",
            "occurred_at": occurred,
        },
    )
    assert micro.status_code == 201, micro.text

    material = client.post(
        f"{ORG}/{user['org_id']}/transactions",
        headers=user["headers"],
        json={
            "transaction_type": "expense",
            "account_id": accounts["checking_id"],
            "category_id": accounts["expense_cat"],
            "amount": "500.00",
            "description": "Renta",
            "occurred_at": occurred,
        },
    )
    assert material.status_code == 201, material.text

    timeline = client.get(
        f"{ORG}/{user['org_id']}/timeline",
        headers=user["headers"],
    )
    assert timeline.status_code == 200, timeline.text
    body = timeline.json()
    titles = [item["title"] for item in body["items"]]
    assert "Ingreso registrado" in titles
    assert "Gasto registrado" in titles
    # Micro expense (low) must not appear
    assert not any(item["description"] == "Cafe" for item in body["items"])
    assert any(item["description"] == "Renta" for item in body["items"])


def test_timeline_commitment_and_goal_events(client: TestClient) -> None:
    user = _register(client)
    accounts = _setup_accounts(client, user)

    debt = client.post(
        f"{ORG}/{user['org_id']}/debts",
        headers=user["headers"],
        json={
            "account_id": accounts["liability_id"],
            "name": "Tarjeta principal",
            "debt_type": "credit_card",
            "priority": "high",
            "interest_rate": "42.00",
            "minimum_payment": "500.00",
            "due_day": 15,
        },
    )
    assert debt.status_code == 201, debt.text

    goal = client.post(
        f"{ORG}/{user['org_id']}/goals",
        headers=user["headers"],
        json={
            "name": "Fondo emergencia",
            "target_amount": "10000.00",
            "currency": "MXN",
            "strategy": "manual",
            "linked_account_ids": [],
        },
    )
    assert goal.status_code == 201, goal.text

    progress = client.post(
        f"{ORG}/{user['org_id']}/goals/{goal.json()['id']}/manual-progress",
        headers=user["headers"],
        json={"current_amount": "2500.00"},
    )
    assert progress.status_code == 200, progress.text

    timeline = client.get(
        f"{ORG}/{user['org_id']}/timeline",
        headers=user["headers"],
        params={"source_type": "commitment"},
    )
    assert timeline.status_code == 200
    assert any(i["event_type"] == "commitment.created" for i in timeline.json()["items"])

    goals_tl = client.get(
        f"{ORG}/{user['org_id']}/timeline",
        headers=user["headers"],
        params={"source_type": "goal"},
    )
    event_types = {i["event_type"] for i in goals_tl.json()["items"]}
    assert "goal.created" in event_types
    assert "goal.milestone_25" in event_types


def test_timeline_cursor_pagination(client: TestClient) -> None:
    user = _register(client)
    accounts = _setup_accounts(client, user)
    base = datetime.now(UTC)

    for i in range(3):
        resp = client.post(
            f"{ORG}/{user['org_id']}/transactions",
            headers=user["headers"],
            json={
                "transaction_type": "income",
                "account_id": accounts["checking_id"],
                "category_id": accounts["income_cat"],
                "amount": "1000.00",
                "description": f"Pago {i}",
                "occurred_at": (base - timedelta(hours=i)).isoformat(),
            },
        )
        assert resp.status_code == 201, resp.text

    page1 = client.get(
        f"{ORG}/{user['org_id']}/timeline",
        headers=user["headers"],
        params={"limit": 2},
    )
    assert page1.status_code == 200
    body1 = page1.json()
    assert len(body1["items"]) == 2
    assert body1["next_cursor"]

    page2 = client.get(
        f"{ORG}/{user['org_id']}/timeline",
        headers=user["headers"],
        params={"limit": 2, "cursor": body1["next_cursor"]},
    )
    assert page2.status_code == 200
    body2 = page2.json()
    assert len(body2["items"]) >= 1
    ids1 = {i["id"] for i in body1["items"]}
    ids2 = {i["id"] for i in body2["items"]}
    assert ids1.isdisjoint(ids2)


def test_dashboard_activity_uses_high_timeline_events(client: TestClient) -> None:
    user = _register(client)
    accounts = _setup_accounts(client, user)
    occurred = datetime.now(UTC).isoformat()

    client.post(
        f"{ORG}/{user['org_id']}/transactions",
        headers=user["headers"],
        json={
            "transaction_type": "income",
            "account_id": accounts["checking_id"],
            "category_id": accounts["income_cat"],
            "amount": "8000.00",
            "description": "Freelance",
            "occurred_at": occurred,
        },
    )

    dash = client.get(
        f"{ORG}/{user['org_id']}/dashboard",
        headers=user["headers"],
        params={"currency": "MXN"},
    )
    assert dash.status_code == 200, dash.text
    activity = dash.json()["widgets"]["activity"]
    assert activity["status"] == "ready"
    assert any(
        item["description"] == "Ingreso registrado" for item in activity["data"]["items"]
    )


def test_timeline_currency_filter_includes_null_currency_events(client: TestClient) -> None:
    user = _register(client)
    accounts = _setup_accounts(client, user)

    debt = client.post(
        f"{ORG}/{user['org_id']}/debts",
        headers=user["headers"],
        json={
            "account_id": accounts["liability_id"],
            "name": "Prestamo",
            "debt_type": "personal_loan",
            "priority": "medium",
            "interest_rate": "18.00",
            "minimum_payment": "1000.00",
        },
    )
    assert debt.status_code == 201, debt.text

    # Pause emits commitment event (currency may be set from debt)
    pause = client.post(
        f"{ORG}/{user['org_id']}/debts/{debt.json()['id']}/pause",
        headers=user["headers"],
    )
    assert pause.status_code == 200

    timeline = client.get(
        f"{ORG}/{user['org_id']}/timeline",
        headers=user["headers"],
        params={"currency": "MXN"},
    )
    assert timeline.status_code == 200
    assert len(timeline.json()["items"]) >= 1


def test_micro_expense_not_projected() -> None:
    from wealthos.modules.timeline.application.builders.transaction_events import (
        MIN_SIGNIFICANT_EXPENSE,
        build_transaction_posted_event,
    )
    from wealthos.modules.transactions.domain.entities.transaction import Transaction
    from wealthos.shared.domain.value_objects.money import Money

    tx = Transaction.create_expense(
        organization_id=uuid4(),
        account_id=uuid4(),
        category_id=uuid4(),
        amount=Money("5.00", "MXN"),
        description="Tip",
        occurred_at=datetime.now(UTC),
        created_by_user_id=uuid4(),
    )
    event = build_transaction_posted_event(tx)
    assert event is not None
    assert event.importance == "low"
    assert MIN_SIGNIFICANT_EXPENSE == Decimal("50.00")
