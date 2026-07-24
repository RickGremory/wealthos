"""Taxes API acceptance tests."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
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


def _register(client: TestClient, org_name: str = "Tax Org") -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"t-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Taxes",
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
    account_type: str = "checking",
) -> dict:
    response = client.post(
        f"{ORG}/{user['org_id']}/accounts",
        headers=user["headers"],
        json={
            "name": name,
            "account_type": account_type,
            "currency": "MXN",
            "opening_balance": opening,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _category(client: TestClient, user: dict, *, type_: str, name: str) -> str:
    items = client.get(
        f"{ORG}/{user['org_id']}/categories",
        headers=user["headers"],
        params={"type": type_},
    ).json()["items"]
    match = next(item for item in items if item["name"] == name)
    return match["id"]


def _create_profile(client: TestClient, user: dict) -> dict:
    response = client.post(
        f"{ORG}/{user['org_id']}/tax-profiles",
        headers=user["headers"],
        json={
            "country_code": "MX",
            "taxpayer_type": "individual",
            "filing_frequency": "monthly",
            "currency": "MXN",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_rule(client: TestClient, user: dict, profile_id: str) -> dict:
    response = client.post(
        f"{ORG}/{user['org_id']}/tax-rules",
        headers=user["headers"],
        json={
            "tax_profile_id": profile_id,
            "name": "ISR 15%",
            "tax_type": "income_tax",
            "calculation_method": "percentage",
            "applies_to": "net_income",
            "effective_from": "2026-01-01",
            "rate": "15.00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_taxes_require_auth(client: TestClient) -> None:
    assert client.get(f"{ORG}/{uuid4()}/tax-profiles").status_code == 401


def test_taxes_require_organization_membership(client: TestClient) -> None:
    user = _register(client)
    response = client.get(f"{ORG}/{uuid4()}/tax-profiles", headers=user["headers"])
    assert response.status_code == 404


def test_create_profile_and_rule(client: TestClient) -> None:
    user = _register(client)
    profile = _create_profile(client, user)
    assert profile["is_active"] is True
    rule = _create_rule(client, user, profile["id"])
    assert rule["rate"] == "15.0000"


def test_calculate_payment_versioning_and_close(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]

    bank = _create_account(client, user, name="HSBC", opening="100000.00")
    profile = _create_profile(client, user)
    _create_rule(client, user, profile["id"])

    income_cat = _category(client, user, type_="income", name="Honorarios")
    expense_cat = _category(client, user, type_="expense", name="Otros gastos")

    client.post(
        f"{ORG}/{org_id}/tax-profiles/{profile['id']}/category-mappings",
        headers=headers,
        json={
            "category_id": income_cat,
            "tax_treatment": "taxable_income",
            "deductibility_percentage": "100",
        },
    )
    client.post(
        f"{ORG}/{org_id}/tax-profiles/{profile['id']}/category-mappings",
        headers=headers,
        json={
            "category_id": expense_cat,
            "tax_treatment": "deductible_expense",
            "deductibility_percentage": "100",
        },
    )

    income = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "income",
            "account_id": bank["id"],
            "category_id": income_cat,
            "amount": "38000.00",
            "description": "Ingreso",
            "occurred_at": datetime(2026, 7, 10, 12, 0, tzinfo=UTC).isoformat(),
        },
    )
    assert income.status_code == 201, income.text
    expense = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "expense",
            "account_id": bank["id"],
            "category_id": expense_cat,
            "amount": "12000.00",
            "description": "Gasto deducible",
            "occurred_at": datetime(2026, 7, 11, 12, 0, tzinfo=UTC).isoformat(),
        },
    )
    assert expense.status_code == 201, expense.text

    periods = client.get(
        f"{ORG}/{org_id}/tax-periods",
        headers=headers,
        params={"tax_profile_id": profile["id"]},
    )
    assert periods.status_code == 200, periods.text
    period_id = periods.json()["items"][0]["id"]

    calc1 = client.post(
        f"{ORG}/{org_id}/tax-periods/{period_id}/calculate",
        headers=headers,
    )
    assert calc1.status_code == 200, calc1.text
    body1 = calc1.json()
    assert body1["version"] == 1
    assert Decimal(str(body1["taxable_base"])) == Decimal("26000.00")
    assert Decimal(str(body1["estimated_tax"])) == Decimal("3900.00")

    calc2 = client.post(
        f"{ORG}/{org_id}/tax-periods/{period_id}/calculate",
        headers=headers,
    )
    assert calc2.status_code == 200, calc2.text
    assert calc2.json()["version"] == 2

    payment = client.post(
        f"{ORG}/{org_id}/tax-periods/{period_id}/payments",
        headers=headers,
        json={
            "source_account_id": bank["id"],
            "amount": "1000.00",
            "tax_type": "income_tax",
            "paid_at": datetime(2026, 7, 15, 12, 0, tzinfo=UTC).isoformat(),
        },
    )
    assert payment.status_code == 201, payment.text
    assert payment.json()["transaction_id"]

    dup = client.post(
        f"{ORG}/{org_id}/tax-periods/{period_id}/payments",
        headers={**headers, "Idempotency-Key": "pay-001"},
        json={
            "source_account_id": bank["id"],
            "amount": "500.00",
            "tax_type": "income_tax",
            "paid_at": datetime(2026, 7, 16, 12, 0, tzinfo=UTC).isoformat(),
        },
    )
    assert dup.status_code == 201, dup.text
    first_id = dup.json()["id"]

    dup2 = client.post(
        f"{ORG}/{org_id}/tax-periods/{period_id}/payments",
        headers={**headers, "Idempotency-Key": "pay-001"},
        json={
            "source_account_id": bank["id"],
            "amount": "500.00",
            "tax_type": "income_tax",
            "paid_at": datetime(2026, 7, 16, 12, 0, tzinfo=UTC).isoformat(),
        },
    )
    assert dup2.status_code == 201
    assert dup2.json()["id"] == first_id

    closed = client.post(
        f"{ORG}/{org_id}/tax-periods/{period_id}/close",
        headers=headers,
    )
    assert closed.status_code == 200, closed.text
    assert closed.json()["status"] == "closed"

    blocked = client.post(
        f"{ORG}/{org_id}/tax-periods/{period_id}/calculate",
        headers=headers,
    )
    assert blocked.status_code == 400


def test_tax_summary_endpoint(client: TestClient) -> None:
    user = _register(client)
    profile = _create_profile(client, user)
    _create_rule(client, user, profile["id"])
    summary = client.get(
        f"{ORG}/{user['org_id']}/taxes/summary",
        headers=user["headers"],
    )
    assert summary.status_code == 200, summary.text
    assert summary.json()["has_active_profile"] is True
