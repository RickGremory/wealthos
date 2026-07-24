"""API integration tests for categories (auth, roles, tenant isolation)."""

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


def _register(client: TestClient, email: str | None = None, org_name: str = "Org") -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": email or f"u-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "User",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    me = client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {token}"}).json()
    orgs = client.get(f"{ME}/organizations", headers={"Authorization": f"Bearer {token}"}).json()
    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": me["id"],
        "org_id": orgs["items"][0]["id"],
    }


def _add_member(
    client: TestClient,
    *,
    owner: dict,
    email: str,
    role: str,
) -> dict:
    member = _register(client, email=email, org_name=f"Other-{uuid4().hex[:6]}")
    add = client.post(
        f"{ORG}/{owner['org_id']}/members",
        headers=owner["headers"],
        json={"user_id": member["user_id"], "role": role},
    )
    assert add.status_code == 201, add.text
    return member


def test_categories_require_auth(client: TestClient) -> None:
    assert client.get(f"{ORG}/{uuid4()}/categories").status_code == 401


def test_non_member_gets_404(client: TestClient) -> None:
    owner = _register(client, org_name="Owner Org")
    stranger = _register(client, org_name="Stranger Org")
    response = client.get(
        f"{ORG}/{owner['org_id']}/categories",
        headers=stranger["headers"],
    )
    assert response.status_code == 404


def test_register_seeds_default_categories(client: TestClient) -> None:
    user = _register(client, org_name="Seed Org")
    listed = client.get(
        f"{ORG}/{user['org_id']}/categories",
        headers=user["headers"],
    )
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] == 20
    assert all(item["is_system"] for item in body["items"])


def test_hierarchy_lifecycle_and_filters(client: TestClient) -> None:
    user = _register(client, org_name="Hierarchy Org")
    org_id = user["org_id"]
    headers = user["headers"]

    create_root = client.post(
        f"{ORG}/{org_id}/categories",
        headers=headers,
        json={"name": "Oficina", "category_type": "expense"},
    )
    assert create_root.status_code == 201, create_root.text
    root = create_root.json()

    create_child = client.post(
        f"{ORG}/{org_id}/categories",
        headers=headers,
        json={
            "name": "Renta",
            "category_type": "expense",
            "parent_id": root["id"],
        },
    )
    assert create_child.status_code == 201, create_child.text
    child = create_child.json()

    third = client.post(
        f"{ORG}/{org_id}/categories",
        headers=headers,
        json={
            "name": "Agua",
            "category_type": "expense",
            "parent_id": child["id"],
        },
    )
    assert third.status_code == 400

    renamed = client.patch(
        f"{ORG}/{org_id}/categories/{child['id']}",
        headers=headers,
        json={"name": "Renta oficina"},
    )
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Renta oficina"

    archive_parent = client.post(
        f"{ORG}/{org_id}/categories/{root['id']}/archive",
        headers=headers,
    )
    assert archive_parent.status_code == 400

    archive_child = client.post(
        f"{ORG}/{org_id}/categories/{child['id']}/archive",
        headers=headers,
    )
    assert archive_child.status_code == 200

    archive_parent_ok = client.post(
        f"{ORG}/{org_id}/categories/{root['id']}/archive",
        headers=headers,
    )
    assert archive_parent_ok.status_code == 200

    expenses = client.get(
        f"{ORG}/{org_id}/categories",
        headers=headers,
        params={"type": "expense", "include_archived": True, "tree": True},
    )
    assert expenses.status_code == 200
    tree = expenses.json()
    assert any(item["name"] == "Oficina" for item in tree["items"])
    assert tree["total"] >= 2


def test_roles_viewer_member_admin(client: TestClient) -> None:
    owner = _register(client, org_name="Roles Org")
    viewer = _add_member(
        client,
        owner=owner,
        email=f"viewer-{uuid4().hex[:8]}@example.com",
        role="viewer",
    )
    member = _add_member(
        client,
        owner=owner,
        email=f"member-{uuid4().hex[:8]}@example.com",
        role="member",
    )
    admin = _add_member(
        client,
        owner=owner,
        email=f"admin-{uuid4().hex[:8]}@example.com",
        role="admin",
    )
    org_id = owner["org_id"]

    listed = client.get(f"{ORG}/{org_id}/categories", headers=viewer["headers"])
    assert listed.status_code == 200

    viewer_create = client.post(
        f"{ORG}/{org_id}/categories",
        headers=viewer["headers"],
        json={"name": "Blocked", "category_type": "income"},
    )
    assert viewer_create.status_code == 403

    member_create = client.post(
        f"{ORG}/{org_id}/categories",
        headers=member["headers"],
        json={"name": "Freelance", "category_type": "income"},
    )
    assert member_create.status_code == 201
    category_id = member_create.json()["id"]

    member_patch = client.patch(
        f"{ORG}/{org_id}/categories/{category_id}",
        headers=member["headers"],
        json={"name": "Freelance renamed"},
    )
    assert member_patch.status_code == 403

    admin_patch = client.patch(
        f"{ORG}/{org_id}/categories/{category_id}",
        headers=admin["headers"],
        json={"name": "Freelance renamed"},
    )
    assert admin_patch.status_code == 200


def test_cross_org_parent_and_get_isolation(client: TestClient) -> None:
    user_a = _register(client, org_name="Org A")
    user_b = _register(client, org_name="Org B")

    parent_a = client.post(
        f"{ORG}/{user_a['org_id']}/categories",
        headers=user_a["headers"],
        json={"name": "Parent A", "category_type": "expense"},
    ).json()

    cross = client.post(
        f"{ORG}/{user_b['org_id']}/categories",
        headers=user_b["headers"],
        json={
            "name": "Child B",
            "category_type": "expense",
            "parent_id": parent_a["id"],
        },
    )
    assert cross.status_code == 404

    get_cross = client.get(
        f"{ORG}/{user_b['org_id']}/categories/{parent_a['id']}",
        headers=user_b["headers"],
    )
    assert get_cross.status_code == 404

    system = client.get(
        f"{ORG}/{user_a['org_id']}/categories",
        headers=user_a["headers"],
        params={"type": "expense"},
    ).json()["items"][0]
    archive_system = client.post(
        f"{ORG}/{user_a['org_id']}/categories/{system['id']}/archive",
        headers=user_a["headers"],
    )
    assert archive_system.status_code == 400
