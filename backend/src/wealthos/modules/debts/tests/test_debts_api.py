"""Debts API acceptance tests."""

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
        session.execute(text("DELETE FROM cash_plan_item_matches"))
        session.execute(text("DELETE FROM cash_plan_items"))
        session.execute(text("DELETE FROM cash_plan_accounts"))
        session.execute(text("DELETE FROM cash_plans"))
        session.execute(text("DELETE FROM budget_allocation_matches"))
        session.execute(text("DELETE FROM budget_allocations"))
        session.execute(text("DELETE FROM budgets"))
        session.execute(text("DELETE FROM mx_tax_calculation_snapshots"))
        session.execute(text("DELETE FROM mx_tax_payment_details"))
        session.execute(text("DELETE FROM mx_transaction_tax_details"))
        session.execute(text("DELETE FROM mx_tax_withholdings"))
        session.execute(text("DELETE FROM tax_evidence"))
        session.execute(text("DELETE FROM mx_tax_transaction_overrides"))
        session.execute(text("DELETE FROM mx_tax_category_mappings"))
        session.execute(text("DELETE FROM mx_tax_configurations"))
        session.execute(text("DELETE FROM mx_tax_catalog_entries"))
        session.execute(text("DELETE FROM tax_calculation_lines"))
        session.execute(text("DELETE FROM tax_calculations"))
        session.execute(text("DELETE FROM tax_payments"))
        session.execute(text("DELETE FROM tax_transaction_overrides"))
        session.execute(text("DELETE FROM tax_category_mappings"))
        session.execute(text("DELETE FROM tax_rule_categories"))
        session.execute(text("DELETE FROM tax_periods"))
        session.execute(text("DELETE FROM tax_rules"))
        session.execute(text("DELETE FROM tax_profiles"))
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


def _register(client: TestClient, org_name: str = "Debts Org") -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"d-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Debts",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    return {"headers": headers, "org_id": org_id}


def _create_account(
    client: TestClient,
    user: dict,
    *,
    name: str,
    opening: str,
    currency: str = "MXN",
    account_type: str = "checking",
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


def _create_debt(
    client: TestClient,
    user: dict,
    *,
    account_id: str,
    name: str = "Tarjeta Nu",
    debt_type: str = "credit_card",
    annual_interest_rate: str = "42.00",
    minimum_payment: str = "2000.00",
) -> dict:
    return client.post(
        f"{ORG}/{user['org_id']}/debts",
        headers=user["headers"],
        json={
            "account_id": account_id,
            "name": name,
            "debt_type": debt_type,
            "annual_interest_rate": annual_interest_rate,
            "minimum_payment": minimum_payment,
        },
    )


def test_debts_require_auth(client: TestClient) -> None:
    assert client.get(f"{ORG}/{uuid4()}/debts").status_code == 401


def test_debts_require_organization_membership(client: TestClient) -> None:
    user = _register(client)
    other_org = uuid4()
    response = client.get(f"{ORG}/{other_org}/debts", headers=user["headers"])
    assert response.status_code == 404


def test_full_debt_payoff_flow(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]

    bank = _create_account(client, user, name="HSBC", opening="50000.00")
    card = _create_account(
        client,
        user,
        name="Tarjeta Nu",
        opening="-25000.00",
        account_type="credit_card",
    )

    created = _create_debt(client, user, account_id=card["id"])
    assert created.status_code == 201, created.text
    debt = created.json()
    assert debt["status"] == "active"
    assert Decimal(str(debt["current_balance"])) == Decimal("25000.00")
    assert debt["is_payment_sufficient"] is True

    payoff = client.get(
        f"{ORG}/{org_id}/debts/payoff-plan",
        headers=headers,
        params={"strategy": "avalanche", "extra_monthly_payment": "5000.00"},
    )
    assert payoff.status_code == 200, payoff.text
    plans = payoff.json()["items"]
    assert len(plans) == 1
    assert plans[0]["currency"] == "MXN"
    assert plans[0]["is_payment_sufficient"] is True
    assert plans[0]["debts"][0]["debt_id"] == debt["id"]

    summary = client.get(f"{ORG}/{org_id}/debts/summary", headers=headers)
    assert summary.status_code == 200, summary.text
    by_currency = summary.json()["by_currency"]
    assert len(by_currency) == 1
    assert Decimal(str(by_currency[0]["total_debt"])) == Decimal("25000.00")
    assert by_currency[0]["active_debt_count"] == 1
    assert by_currency[0]["highest_interest_debt_id"] == debt["id"]

    first_payment = client.post(
        f"{ORG}/{org_id}/debts/{debt['id']}/payments",
        headers=headers,
        json={
            "source_account_id": bank["id"],
            "amount": "10000.00",
            "occurred_at": "2026-07-20T12:00:00Z",
        },
    )
    assert first_payment.status_code == 201, first_payment.text

    bank_after = client.get(f"{ORG}/{org_id}/accounts/{bank['id']}", headers=headers).json()
    card_after = client.get(f"{ORG}/{org_id}/accounts/{card['id']}", headers=headers).json()
    assert Decimal(str(bank_after["current_balance"])) == Decimal("40000.00")
    assert Decimal(str(card_after["current_balance"])) == Decimal("-15000.00")

    debt_after_first = client.get(f"{ORG}/{org_id}/debts/{debt['id']}", headers=headers).json()
    assert debt_after_first["status"] == "active"
    assert Decimal(str(debt_after_first["current_balance"])) == Decimal("15000.00")

    second_payment = client.post(
        f"{ORG}/{org_id}/debts/{debt['id']}/payments",
        headers=headers,
        json={
            "source_account_id": bank["id"],
            "amount": "15000.00",
            "occurred_at": "2026-07-21T12:00:00Z",
        },
    )
    assert second_payment.status_code == 201, second_payment.text

    debt_after_second = client.get(f"{ORG}/{org_id}/debts/{debt['id']}", headers=headers).json()
    assert debt_after_second["status"] == "paid_off"
    assert Decimal(str(debt_after_second["current_balance"])) == Decimal("0.00")

    payments = client.get(
        f"{ORG}/{org_id}/debts/{debt['id']}/payments",
        headers=headers,
    ).json()
    assert payments["total"] == 2


def test_reject_debt_on_asset_account(client: TestClient) -> None:
    user = _register(client)
    savings = _create_account(client, user, name="Ahorro", opening="0.00")
    response = _create_debt(client, user, account_id=savings["id"])
    assert response.status_code == 400, response.text


def test_reject_second_active_debt_for_same_account(client: TestClient) -> None:
    user = _register(client)
    card = _create_account(
        client,
        user,
        name="Tarjeta",
        opening="-1000.00",
        account_type="credit_card",
    )
    first = _create_debt(client, user, account_id=card["id"])
    assert first.status_code == 201, first.text

    second = _create_debt(client, user, account_id=card["id"], name="Duplicada")
    assert second.status_code == 409, second.text


def test_reject_overpayment_beyond_outstanding_balance(client: TestClient) -> None:
    user = _register(client)
    headers = user["headers"]
    org_id = user["org_id"]
    bank = _create_account(client, user, name="Banco", opening="10000.00")
    card = _create_account(
        client,
        user,
        name="Tarjeta",
        opening="-1000.00",
        account_type="credit_card",
    )
    debt = _create_debt(client, user, account_id=card["id"]).json()

    response = client.post(
        f"{ORG}/{org_id}/debts/{debt['id']}/payments",
        headers=headers,
        json={
            "source_account_id": bank["id"],
            "amount": "1500.00",
            "occurred_at": "2026-07-20T12:00:00Z",
        },
    )
    assert response.status_code == 400, response.text


def test_get_and_archive_debt_not_found(client: TestClient) -> None:
    user = _register(client)
    headers = user["headers"]
    org_id = user["org_id"]
    missing_id = uuid4()

    get_response = client.get(f"{ORG}/{org_id}/debts/{missing_id}", headers=headers)
    assert get_response.status_code == 404

    archive_response = client.post(
        f"{ORG}/{org_id}/debts/{missing_id}/archive",
        headers=headers,
    )
    assert archive_response.status_code == 404


def test_update_and_archive_debt(client: TestClient) -> None:
    user = _register(client)
    headers = user["headers"]
    org_id = user["org_id"]
    card = _create_account(
        client,
        user,
        name="Tarjeta",
        opening="-2000.00",
        account_type="credit_card",
    )
    debt = _create_debt(client, user, account_id=card["id"]).json()

    updated = client.patch(
        f"{ORG}/{org_id}/debts/{debt['id']}",
        headers=headers,
        json={"minimum_payment": "750.00", "notes": "Renegociada"},
    )
    assert updated.status_code == 200, updated.text
    assert Decimal(str(updated.json()["minimum_payment"])) == Decimal("750.00")
    assert updated.json()["notes"] == "Renegociada"

    archived = client.post(f"{ORG}/{org_id}/debts/{debt['id']}/archive", headers=headers)
    assert archived.status_code == 200, archived.text
    assert archived.json()["status"] == "archived"

    listed = client.get(f"{ORG}/{org_id}/debts", headers=headers).json()
    assert listed["total"] == 0
    with_archived = client.get(
        f"{ORG}/{org_id}/debts",
        headers=headers,
        params={"include_archived": True},
    ).json()
    assert with_archived["total"] == 1


def test_list_debts_filters_by_debt_type(client: TestClient) -> None:
    user = _register(client)
    headers = user["headers"]
    org_id = user["org_id"]
    card = _create_account(
        client,
        user,
        name="Tarjeta",
        opening="-2000.00",
        account_type="credit_card",
    )
    loan_account = _create_account(
        client,
        user,
        name="Prestamo",
        opening="-8000.00",
        account_type="loan",
    )
    _create_debt(client, user, account_id=card["id"], debt_type="credit_card")
    _create_debt(client, user, account_id=loan_account["id"], debt_type="personal_loan")

    only_cards = client.get(
        f"{ORG}/{org_id}/debts",
        headers=headers,
        params={"debt_type": "credit_card"},
    ).json()
    assert only_cards["total"] == 1
    assert only_cards["items"][0]["debt_type"] == "credit_card"
