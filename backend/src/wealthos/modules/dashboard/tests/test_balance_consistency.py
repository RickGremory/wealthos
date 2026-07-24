"""Helper and test: current_balance matches opening + posted entries."""

from __future__ import annotations

from collections.abc import Generator
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text

from wealthos.core.database import SessionLocal
from wealthos.main import app
from wealthos.modules.accounts.infrastructure.models.account_model import AccountModel
from wealthos.modules.transactions.infrastructure.models.transaction_model import (
    TransactionEntryModel,
    TransactionModel,
)

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


def recalculate_account_balance(session, account_id) -> Decimal:  # noqa: ANN001
    account = session.get(AccountModel, account_id)
    assert account is not None
    entries_sum = session.scalar(
        select(func.coalesce(func.sum(TransactionEntryModel.amount), 0)).where(
            TransactionEntryModel.account_id == account_id,
            TransactionEntryModel.transaction_id.in_(
                select(TransactionModel.id).where(TransactionModel.status == "posted")
            ),
        )
    )
    return Decimal(str(account.opening_balance)) + Decimal(str(entries_sum or 0))


def test_current_balance_matches_recalculated(client: TestClient) -> None:
    register = client.post(
        f"{AUTH}/register",
        json={
            "email": f"b-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "Bal",
            "organization_name": "Balance Org",
        },
    )
    headers = {"Authorization": f"Bearer {register.json()['access_token']}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    income_cat = client.get(
        f"{ORG}/{org_id}/categories",
        headers=headers,
        params={"type": "income"},
    ).json()["items"][0]["id"]
    account = client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "Cash",
            "account_type": "cash",
            "currency": "MXN",
            "opening_balance": "1000.00",
        },
    ).json()
    client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "income",
            "account_id": account["id"],
            "category_id": income_cat,
            "amount": "250.00",
            "description": "Top up",
            "occurred_at": "2026-07-10T12:00:00Z",
        },
    )

    with SessionLocal() as session:
        expected = recalculate_account_balance(session, account["id"])
        stored = session.get(AccountModel, account["id"])
        assert stored is not None
        assert Decimal(str(stored.current_balance)) == expected
        assert expected == Decimal("1250.00")
