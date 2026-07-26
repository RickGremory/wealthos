"""Legal API acceptance tests."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from wealthos.core.database import SessionLocal
from wealthos.main import app
from wealthos.modules.legal.tests.register_helpers import DEFAULT_LEGAL_ACCEPTANCES

AUTH = "/api/v1/auth"
LEGAL = "/api/v1/legal"


@pytest.fixture()
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def _reset_legal_state(session) -> None:
    # Full dependency chain so leftover rows from other suites don't block cleanup.
    for stmt in (
        "DELETE FROM cash_plan_item_matches",
        "DELETE FROM cash_plan_items",
        "DELETE FROM cash_plan_accounts",
        "DELETE FROM cash_plans",
        "DELETE FROM budget_allocation_matches",
        "DELETE FROM budget_allocations",
        "DELETE FROM budgets",
        "DELETE FROM timeline_events",
        "DELETE FROM debt_payments",
        "DELETE FROM debts",
        "DELETE FROM goal_manual_progress",
        "DELETE FROM goal_accounts",
        "DELETE FROM goals",
        "DELETE FROM transaction_entries",
        "DELETE FROM transactions",
        "DELETE FROM legal_consents",
        "DELETE FROM categories",
        "DELETE FROM accounts",
        "DELETE FROM organization_memberships",
        "DELETE FROM organizations",
        "DELETE FROM users",
        "DELETE FROM legal_documents WHERE version <> '1.0'",
    ):
        session.execute(text(stmt))
    session.execute(
        text(
            """
            UPDATE legal_documents
            SET is_active = true, requires_reacceptance = false
            WHERE version = '1.0'
            """
        )
    )
    session.commit()


@pytest.fixture(autouse=True)
def _cleanup() -> Generator[None]:
    with SessionLocal() as session:
        _reset_legal_state(session)
    yield
    with SessionLocal() as session:
        _reset_legal_state(session)


def _register(client: TestClient, **overrides: object) -> dict:
    payload = {
        "email": f"legal-{uuid4().hex[:8]}@example.com",
        "password": "WealthOS-2026-Segura",
        "display_name": "Legal User",
        "organization_name": "Legal Org",
        "legal_acceptances": list(DEFAULT_LEGAL_ACCEPTANCES),
        "marketing_consent": False,
    }
    payload.update(overrides)
    response = client.post(f"{AUTH}/register", json=payload)
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    return {"headers": {"Authorization": f"Bearer {token}"}, "token": token}


def test_registration_requirements_public(client: TestClient) -> None:
    response = client.get(f"{LEGAL}/registration-requirements")
    assert response.status_code == 200, response.text
    body = response.json()
    types = {d["type"] for d in body["documents"]}
    assert types == {"terms_of_service", "privacy_notice"}
    assert body["marketing_consent"] == {"available": True, "required": False}


def test_register_without_terms_fails(client: TestClient) -> None:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"nolegal-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "No Legal",
            "organization_name": "No Legal Org",
            "legal_acceptances": [
                {
                    "document_type": "privacy_notice",
                    "version": "1.0",
                    "acknowledged": True,
                }
            ],
        },
    )
    assert response.status_code == 422, response.text
    detail = response.json()["detail"]
    assert detail["code"] == "LEGAL_ACCEPTANCE_REQUIRED"


def test_register_wrong_version_returns_409(client: TestClient) -> None:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"oldver-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Old Ver",
            "organization_name": "Old Ver Org",
            "legal_acceptances": [
                {
                    "document_type": "terms_of_service",
                    "version": "0.9",
                    "accepted": True,
                },
                {
                    "document_type": "privacy_notice",
                    "version": "1.0",
                    "acknowledged": True,
                },
            ],
        },
    )
    assert response.status_code == 409, response.text
    assert response.json()["detail"]["code"] == "LEGAL_DOCUMENT_VERSION_OUTDATED"


def test_register_success_creates_consents(client: TestClient) -> None:
    user = _register(client, marketing_consent=True)
    status = client.get(f"{LEGAL}/me/status", headers=user["headers"])
    assert status.status_code == 200, status.text
    assert status.json()["is_compliant"] is True
    assert status.json()["pending_documents"] == []

    docs = client.get(f"{LEGAL}/me/documents", headers=user["headers"])
    assert docs.status_code == 200, docs.text
    body = docs.json()
    assert body["marketing_consent"]["opted_in"] is True
    types = {d["type"] for d in body["documents"]}
    assert "terms_of_service" in types
    assert "privacy_notice" in types


def test_me_status_pending_after_requires_reacceptance(client: TestClient) -> None:
    user = _register(client)
    assert client.get(f"{LEGAL}/me/status", headers=user["headers"]).json()["is_compliant"]

    now = datetime.now(UTC)
    new_id = str(uuid4())
    with SessionLocal() as session:
        session.execute(
            text("UPDATE legal_documents SET is_active = false WHERE document_type = 'terms_of_service'")
        )
        session.execute(
            text(
                """
                INSERT INTO legal_documents (
                    id, document_type, version, title, content_url, content_markdown,
                    content_hash, effective_at, published_at, is_active,
                    requires_reacceptance, change_summary, created_at
                ) VALUES (
                    :id, 'terms_of_service', '1.1', 'Términos de servicio',
                    '/legal/terms', 'Borrador v1.1', :hash,
                    :now, :now, true, true, 'Actualización de prueba', :now
                )
                """
            ),
            {
                "id": new_id,
                "hash": "a" * 64,
                "now": now,
            },
        )
        session.commit()

    status = client.get(f"{LEGAL}/me/status", headers=user["headers"])
    assert status.status_code == 200, status.text
    body = status.json()
    assert body["is_compliant"] is False
    pending_types = {p["type"] for p in body["pending_documents"]}
    assert "terms_of_service" in pending_types

    accept = client.post(
        f"{LEGAL}/me/acceptances",
        headers=user["headers"],
        json={
            "acceptances": [
                {
                    "document_type": "terms_of_service",
                    "version": "1.1",
                    "accepted": True,
                }
            ]
        },
    )
    assert accept.status_code == 200, accept.text
    assert accept.json()["is_compliant"] is True


def test_get_active_document_public(client: TestClient) -> None:
    response = client.get(f"{LEGAL}/documents/privacy_notice")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["type"] == "privacy_notice"
    assert body["version"] == "1.0"
    assert "Borrador" in body["content_markdown"]
