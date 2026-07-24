"""Planning API acceptance tests (budgets + cash plans)."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, date, datetime
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

_PLANNING_DELETE = (
    "DELETE FROM cash_plan_item_matches",
    "DELETE FROM cash_plan_items",
    "DELETE FROM cash_plan_accounts",
    "DELETE FROM cash_plans",
    "DELETE FROM budget_allocation_matches",
    "DELETE FROM budget_allocations",
    "DELETE FROM budgets",
)


@pytest.fixture()
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _cleanup() -> Generator[None]:
    yield
    with SessionLocal() as session:
        for stmt in _PLANNING_DELETE:
            session.execute(text(stmt))
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


def _register(client: TestClient, org_name: str = "Planning Org") -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"p-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Planner",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get(f"{AUTH}/me", headers=headers).json()
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    return {"headers": headers, "org_id": org_id, "user_id": me["id"], "token": token}


def _create_account(
    client: TestClient,
    user: dict,
    *,
    name: str = "HSBC",
    opening: str = "50000.00",
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


def _category_id(client: TestClient, user: dict, *, name: str, category_type: str) -> str:
    listed = client.get(f"{ORG}/{user['org_id']}/categories", headers=user["headers"])
    assert listed.status_code == 200, listed.text
    for item in listed.json()["items"]:
        if item["name"] == name and item["category_type"] == category_type:
            return item["id"]
    raise AssertionError(f"Category {name!r} ({category_type}) not found in seed")


def _post_expense(
    client: TestClient,
    user: dict,
    *,
    account_id: str,
    category_id: str,
    amount: str,
    occurred_at: datetime | None = None,
) -> dict:
    when = occurred_at or datetime.now(UTC)
    response = client.post(
        f"{ORG}/{user['org_id']}/transactions",
        headers=user["headers"],
        json={
            "transaction_type": "expense",
            "account_id": account_id,
            "category_id": category_id,
            "amount": amount,
            "description": "Gasto prueba",
            "occurred_at": when.isoformat(),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _post_income(
    client: TestClient,
    user: dict,
    *,
    account_id: str,
    category_id: str,
    amount: str,
    occurred_at: datetime | None = None,
) -> dict:
    when = occurred_at or datetime.now(UTC)
    response = client.post(
        f"{ORG}/{user['org_id']}/transactions",
        headers=user["headers"],
        json={
            "transaction_type": "income",
            "account_id": account_id,
            "category_id": category_id,
            "amount": amount,
            "description": "Ingreso prueba",
            "occurred_at": when.isoformat(),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_budgets_require_auth(client: TestClient) -> None:
    assert client.get(f"{ORG}/{uuid4()}/budgets").status_code == 401


def test_create_activate_allocations_and_list(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    income_cat = _category_id(client, user, name="Honorarios", category_type="income")
    food_cat = _category_id(client, user, name="Alimentación", category_type="expense")

    created = client.post(
        f"{ORG}/{org_id}/budgets",
        headers=headers,
        json={
            "name": "Presupuesto MXN",
            "period_type": "monthly",
            "currency": "MXN",
            "reference_date": date.today().isoformat(),
        },
    )
    assert created.status_code == 201, created.text
    budget = created.json()
    assert budget["status"] == "draft"
    budget_id = budget["id"]

    activated = client.post(
        f"{ORG}/{org_id}/budgets/{budget_id}/activate",
        headers=headers,
    )
    assert activated.status_code == 200, activated.text
    assert activated.json()["status"] == "active"

    income = client.post(
        f"{ORG}/{org_id}/budgets/{budget_id}/allocations",
        headers=headers,
        json={
            "allocation_type": "income",
            "amount": "50000.00",
            "category_id": income_cat,
        },
    )
    assert income.status_code == 201, income.text

    expense = client.post(
        f"{ORG}/{org_id}/budgets/{budget_id}/allocations",
        headers=headers,
        json={
            "allocation_type": "expense",
            "amount": "8000.00",
            "category_id": food_cat,
        },
    )
    assert expense.status_code == 201, expense.text

    listed = client.get(f"{ORG}/{org_id}/budgets", headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] >= 1
    assert any(item["id"] == budget_id for item in listed.json()["items"])

    detail = client.get(f"{ORG}/{org_id}/budgets/{budget_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    assert len(detail.json()["allocations"]) == 2


def test_budget_performance_utilization_and_over_budget(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    account = _create_account(client, user)
    food_cat = _category_id(client, user, name="Alimentación", category_type="expense")
    today = date.today()
    # Noon UTC mid-period avoids timezone edge cases vs date.today() local cutoffs.
    mid_month = datetime(today.year, today.month, min(today.day, 28), 12, 0, tzinfo=UTC)

    created = client.post(
        f"{ORG}/{org_id}/budgets",
        headers=headers,
        json={
            "name": "Food budget",
            "period_type": "monthly",
            "currency": "MXN",
            "reference_date": today.isoformat(),
        },
    )
    assert created.status_code == 201, created.text
    budget_id = created.json()["id"]
    assert (
        client.post(f"{ORG}/{org_id}/budgets/{budget_id}/activate", headers=headers).status_code
        == 200
    )

    allocation = client.post(
        f"{ORG}/{org_id}/budgets/{budget_id}/allocations",
        headers=headers,
        json={
            "allocation_type": "expense",
            "amount": "8000.00",
            "category_id": food_cat,
        },
    )
    assert allocation.status_code == 201, allocation.text
    allocation_id = allocation.json()["id"]

    _post_expense(
        client,
        user,
        account_id=account["id"],
        category_id=food_cat,
        amount="3000.00",
        occurred_at=mid_month,
    )

    perf = client.get(f"{ORG}/{org_id}/budgets/{budget_id}/performance", headers=headers)
    assert perf.status_code == 200, perf.text
    body = perf.json()
    food_row = next(a for a in body["allocations"] if a["allocation_id"] == allocation_id)
    assert Decimal(str(food_row["planned_amount"])) == Decimal("8000.00")
    assert Decimal(str(food_row["actual_amount"])) == Decimal("3000.00")
    assert Decimal(str(food_row["utilization_percentage"])) == Decimal("37.50")

    _post_expense(
        client,
        user,
        account_id=account["id"],
        category_id=food_cat,
        amount="6000.00",
        occurred_at=mid_month,
    )
    over = client.get(f"{ORG}/{org_id}/budgets/{budget_id}/performance", headers=headers)
    assert over.status_code == 200, over.text
    over_row = next(a for a in over.json()["allocations"] if a["allocation_id"] == allocation_id)
    assert Decimal(str(over_row["actual_amount"])) == Decimal("9000.00")
    assert over_row["status"] == "over_budget"


def test_closed_budget_rejects_new_allocations(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    food_cat = _category_id(client, user, name="Alimentación", category_type="expense")

    created = client.post(
        f"{ORG}/{org_id}/budgets",
        headers=headers,
        json={
            "name": "Close me",
            "period_type": "monthly",
            "currency": "MXN",
            "reference_date": date.today().isoformat(),
        },
    )
    budget_id = created.json()["id"]
    client.post(f"{ORG}/{org_id}/budgets/{budget_id}/activate", headers=headers)
    closed = client.post(f"{ORG}/{org_id}/budgets/{budget_id}/close", headers=headers)
    assert closed.status_code == 200, closed.text
    assert closed.json()["status"] == "closed"

    blocked = client.post(
        f"{ORG}/{org_id}/budgets/{budget_id}/allocations",
        headers=headers,
        json={
            "allocation_type": "expense",
            "amount": "100.00",
            "category_id": food_cat,
        },
    )
    assert blocked.status_code in {400, 403, 422}, blocked.text


def test_cash_plan_projection_detects_temporary_shortfall(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]

    created = client.post(
        f"{ORG}/{org_id}/cash-plans",
        headers=headers,
        json={
            "name": "Aug cash",
            "date_from": "2026-08-01",
            "date_to": "2026-08-20",
            "currency": "MXN",
            "opening_balance_mode": "manual",
            "manual_opening_balance": "20000.00",
        },
    )
    assert created.status_code == 201, created.text
    plan = created.json()
    assert plan["status"] == "active"
    plan_id = plan["id"]

    for payload in (
        {
            "item_type": "outflow",
            "description": "Tax",
            "expected_date": "2026-08-10",
            "amount": "25000.00",
            "probability": "100",
        },
        {
            "item_type": "outflow",
            "description": "Rent",
            "expected_date": "2026-08-12",
            "amount": "10000.00",
            "probability": "100",
        },
        {
            "item_type": "inflow",
            "description": "Invoice",
            "expected_date": "2026-08-15",
            "amount": "30000.00",
            "probability": "100",
        },
    ):
        item = client.post(
            f"{ORG}/{org_id}/cash-plans/{plan_id}/items",
            headers=headers,
            json=payload,
        )
        assert item.status_code == 201, item.text

    projection = client.get(
        f"{ORG}/{org_id}/cash-plans/{plan_id}/projection",
        headers=headers,
        params={"scenario": "expected", "granularity": "day"},
    )
    assert projection.status_code == 200, projection.text
    body = projection.json()
    assert Decimal(str(body["opening_balance"])) == Decimal("20000.00")
    assert Decimal(str(body["ending_balance"])) == Decimal("15000.00")
    assert Decimal(str(body["minimum_balance"])) == Decimal("-15000.00")
    assert body["first_shortfall_date"] == "2026-08-10"
    assert Decimal(str(body["ending_balance"])) > 0
    assert Decimal(str(body["minimum_balance"])) < 0


def test_partial_match_updates_projection(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    account = _create_account(client, user, opening="0.00")
    income_cat = _category_id(client, user, name="Honorarios", category_type="income")

    created = client.post(
        f"{ORG}/{org_id}/cash-plans",
        headers=headers,
        json={
            "name": "Match plan",
            "date_from": "2026-08-01",
            "date_to": "2026-08-15",
            "currency": "MXN",
            "opening_balance_mode": "manual",
            "manual_opening_balance": "0.00",
        },
    )
    plan_id = created.json()["id"]
    item = client.post(
        f"{ORG}/{org_id}/cash-plans/{plan_id}/items",
        headers=headers,
        json={
            "item_type": "inflow",
            "description": "Big invoice",
            "expected_date": "2026-08-10",
            "amount": "50000.00",
        },
    )
    assert item.status_code == 201, item.text
    item_id = item.json()["id"]

    before = client.get(
        f"{ORG}/{org_id}/cash-plans/{plan_id}/projection",
        headers=headers,
        params={"scenario": "optimistic"},
    ).json()
    by_date_before = {p["date"]: p for p in before["points"]}
    assert Decimal(str(by_date_before["2026-08-10"]["inflows"])) == Decimal("50000.00")

    tx = _post_income(
        client,
        user,
        account_id=account["id"],
        category_id=income_cat,
        amount="30000.00",
        occurred_at=datetime(2026, 8, 9, 12, 0, tzinfo=UTC),
    )
    matched = client.post(
        f"{ORG}/{org_id}/cash-plans/{plan_id}/items/{item_id}/match",
        headers=headers,
        json={"transaction_id": tx["id"], "matched_amount": "30000.00"},
    )
    assert matched.status_code == 201, matched.text

    after = client.get(
        f"{ORG}/{org_id}/cash-plans/{plan_id}/projection",
        headers=headers,
        params={"scenario": "optimistic"},
    ).json()
    by_date = {p["date"]: p for p in after["points"]}
    assert Decimal(str(by_date["2026-08-09"]["inflows"])) == Decimal("30000.00")
    assert Decimal(str(by_date["2026-08-10"]["inflows"])) == Decimal("20000.00")


def test_probability_validation_rejection(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]
    created = client.post(
        f"{ORG}/{org_id}/cash-plans",
        headers=headers,
        json={
            "name": "Prob plan",
            "date_from": "2026-08-01",
            "date_to": "2026-08-31",
            "currency": "MXN",
            "opening_balance_mode": "manual",
            "manual_opening_balance": "1000.00",
        },
    )
    plan_id = created.json()["id"]
    bad = client.post(
        f"{ORG}/{org_id}/cash-plans/{plan_id}/items",
        headers=headers,
        json={
            "item_type": "inflow",
            "description": "Bad prob",
            "expected_date": "2026-08-10",
            "amount": "1000.00",
            "probability": "150",
        },
    )
    assert bad.status_code == 422, bad.text


def test_planning_summary_returns_currency_fields(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]

    budget = client.post(
        f"{ORG}/{org_id}/budgets",
        headers=headers,
        json={
            "name": "Summary budget",
            "period_type": "monthly",
            "currency": "MXN",
            "reference_date": date.today().isoformat(),
        },
    )
    assert budget.status_code == 201, budget.text
    client.post(
        f"{ORG}/{org_id}/budgets/{budget.json()['id']}/activate",
        headers=headers,
    )

    plan = client.post(
        f"{ORG}/{org_id}/cash-plans",
        headers=headers,
        json={
            "name": "Summary cash",
            "date_from": date.today().isoformat(),
            "date_to": date.today().isoformat(),
            "currency": "MXN",
            "opening_balance_mode": "manual",
            "manual_opening_balance": "5000.00",
        },
    )
    assert plan.status_code == 201, plan.text

    summary = client.get(f"{ORG}/{org_id}/planning/summary", headers=headers)
    assert summary.status_code == 200, summary.text
    body = summary.json()
    assert body["active_budgets"] >= 1
    assert body["active_cash_plans"] >= 1
    assert body["currency"] == "MXN"
    assert body["primary_cash_plan_id"] == plan.json()["id"]
    assert "safe_to_spend" in body
    assert "funding_gap" in body


def test_viewer_can_get_member_can_post(client: TestClient) -> None:
    owner = _register(client, org_name="Owner Planning")
    viewer = _register(client, org_name="Viewer Personal")
    add = client.post(
        f"{ORG}/{owner['org_id']}/members",
        headers=owner["headers"],
        json={"user_id": viewer["user_id"], "role": "viewer"},
    )
    assert add.status_code == 201, add.text

    listed = client.get(
        f"{ORG}/{owner['org_id']}/budgets",
        headers=viewer["headers"],
    )
    assert listed.status_code == 200, listed.text

    denied = client.post(
        f"{ORG}/{owner['org_id']}/budgets",
        headers=viewer["headers"],
        json={
            "name": "Viewer budget",
            "period_type": "monthly",
            "currency": "MXN",
            "reference_date": date.today().isoformat(),
        },
    )
    assert denied.status_code == 403, denied.text

    # Owner (member-capable role) can create.
    created = client.post(
        f"{ORG}/{owner['org_id']}/budgets",
        headers=owner["headers"],
        json={
            "name": "Owner budget",
            "period_type": "monthly",
            "currency": "MXN",
            "reference_date": date.today().isoformat(),
        },
    )
    assert created.status_code == 201, created.text


def test_cannot_match_transaction_from_another_org(client: TestClient) -> None:
    user_a = _register(client, org_name="Org A Planning")
    user_b = _register(client, org_name="Org B Planning")
    account_b = _create_account(client, user_b)
    income_cat_b = _category_id(client, user_b, name="Honorarios", category_type="income")
    tx_b = _post_income(
        client,
        user_b,
        account_id=account_b["id"],
        category_id=income_cat_b,
        amount="1000.00",
    )

    plan = client.post(
        f"{ORG}/{user_a['org_id']}/cash-plans",
        headers=user_a["headers"],
        json={
            "name": "A plan",
            "date_from": "2026-08-01",
            "date_to": "2026-08-31",
            "currency": "MXN",
            "opening_balance_mode": "manual",
            "manual_opening_balance": "0.00",
        },
    )
    plan_id = plan.json()["id"]
    item = client.post(
        f"{ORG}/{user_a['org_id']}/cash-plans/{plan_id}/items",
        headers=user_a["headers"],
        json={
            "item_type": "inflow",
            "description": "Expected",
            "expected_date": "2026-08-10",
            "amount": "1000.00",
        },
    )
    item_id = item.json()["id"]

    match = client.post(
        f"{ORG}/{user_a['org_id']}/cash-plans/{plan_id}/items/{item_id}/match",
        headers=user_a["headers"],
        json={"transaction_id": tx_b["id"], "matched_amount": "1000.00"},
    )
    assert match.status_code in {400, 404}, match.text
