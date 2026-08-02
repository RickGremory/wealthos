"""Smoke tests for Recurring HTTP API."""

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


def _register(client: TestClient, org_name: str = "Recurring Org") -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"r-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Recurring",
            "organization_name": org_name,
            "legal_acceptances": [
                {
                    "document_type": "terms_of_service",
                    "version": "1.0",
                    "accepted": True,
                },
                {
                    "document_type": "privacy_notice",
                    "version": "1.0",
                    "acknowledged": True,
                },
            ],
            "marketing_consent": False,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get(f"{AUTH}/me", headers=headers).json()
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    return {"headers": headers, "org_id": org_id, "user_id": me["id"]}


def _rule_body(**overrides):
    body = {
        "name": "Internet",
        "direction": "outflow",
        "amount": "800.00",
        "currency": "MXN",
        "starts_on": "2026-07-15",
        "pattern": {
            "frequency": "monthly",
            "interval": 1,
            "day_of_month": 15,
            "end_of_month": False,
        },
    }
    body.update(overrides)
    return body


def test_create_list_preview_flow(client: TestClient) -> None:
    user = _register(client)

    preview = client.post(
        f"{ORG}/{user['org_id']}/recurring/preview",
        headers=user["headers"],
        json={
            "name": "Internet",
            "direction": "outflow",
            "amount": "800.00",
            "currency": "MXN",
            "starts_on": "2026-07-15",
            "from": "2026-08-01",
            "to": "2026-10-31",
            "pattern": {
                "frequency": "monthly",
                "interval": 1,
                "day_of_month": 15,
                "end_of_month": False,
            },
        },
    )
    assert preview.status_code == 200, preview.text
    assert preview.json()["dates"] == ["2026-08-15", "2026-09-15", "2026-10-15"]

    created = client.post(
        f"{ORG}/{user['org_id']}/recurring",
        headers=user["headers"],
        json=_rule_body(),
    )
    assert created.status_code == 201, created.text
    rule_id = created.json()["id"]

    listed = client.get(f"{ORG}/{user['org_id']}/recurring", headers=user["headers"])
    assert listed.status_code == 200, listed.text
    assert len(listed.json()) == 1

    occurrences = client.get(
        f"{ORG}/{user['org_id']}/recurring/occurrences",
        headers=user["headers"],
        params={"from": "2026-08-01", "to": "2026-09-30", "currency": "MXN"},
    )
    assert occurrences.status_code == 200, occurrences.text
    assert [item["expected_on"] for item in occurrences.json()] == [
        "2026-08-15",
        "2026-09-15",
    ]

    detail = client.get(
        f"{ORG}/{user['org_id']}/recurring/{rule_id}",
        headers=user["headers"],
    )
    assert detail.status_code == 200, detail.text
    assert detail.json()["name"] == "Internet"

    timeline = client.get(
        f"{ORG}/{user['org_id']}/timeline",
        headers=user["headers"],
        params={"source_type": "recurring"},
    )
    assert timeline.status_code == 200, timeline.text
    events = timeline.json().get("items") or timeline.json()
    if isinstance(events, dict):
        events = events.get("items", [])
    assert any(e.get("event_type") == "recurring.rule.created" for e in events)


def test_viewer_can_get_member_cannot_archive(client: TestClient) -> None:
    owner = _register(client, org_name="Owner Recurring")
    viewer = _register(client, org_name="Viewer Personal")
    add = client.post(
        f"{ORG}/{owner['org_id']}/members",
        headers=owner["headers"],
        json={"user_id": viewer["user_id"], "role": "viewer"},
    )
    assert add.status_code == 201, add.text

    created = client.post(
        f"{ORG}/{owner['org_id']}/recurring",
        headers=owner["headers"],
        json=_rule_body(),
    )
    assert created.status_code == 201, created.text
    rule = created.json()
    rule_id = rule["id"]
    version = rule["version"]

    listed = client.get(
        f"{ORG}/{owner['org_id']}/recurring",
        headers=viewer["headers"],
    )
    assert listed.status_code == 200, listed.text

    denied_create = client.post(
        f"{ORG}/{owner['org_id']}/recurring",
        headers=viewer["headers"],
        json=_rule_body(name="Viewer rule"),
    )
    assert denied_create.status_code == 403, denied_create.text

    member = _register(client, org_name="Member Personal")
    add_member = client.post(
        f"{ORG}/{owner['org_id']}/members",
        headers=owner["headers"],
        json={"user_id": member["user_id"], "role": "member"},
    )
    assert add_member.status_code == 201, add_member.text

    denied_archive = client.post(
        f"{ORG}/{owner['org_id']}/recurring/{rule_id}/archive",
        headers=member["headers"],
        json={"expected_version": version},
    )
    assert denied_archive.status_code == 403, denied_archive.text

    archived = client.post(
        f"{ORG}/{owner['org_id']}/recurring/{rule_id}/archive",
        headers=owner["headers"],
        json={"expected_version": version},
    )
    assert archived.status_code == 200, archived.text
    assert archived.json()["status"] == "archived"

