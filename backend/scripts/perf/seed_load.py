#!/usr/bin/env python3
"""Seed a dedicated load-test organization with tens of thousands of transactions.

Usage (from backend/):
  uv run python scripts/perf/seed_load.py
  uv run python scripts/perf/seed_load.py --transactions 50000 --accounts 30

Credentials printed at the end for benchmark_http.py.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

# Allow running as `python scripts/perf/seed_load.py`
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

# Keep seed output readable (avoid SQLAlchemy echo flood).
os.environ.setdefault("DB_ECHO", "false")
os.environ.setdefault("DEBUG", "false")

from wealthos.core.database import SessionLocal  # noqa: E402
from wealthos.main import app  # noqa: E402

AUTH = "/api/v1/auth"
ME = "/api/v1/me"
ORG = "/api/v1/organizations"

LOAD_EMAIL = "loadtest@wealthos.local"
LOAD_PASSWORD = "WealthOS-Load-2026"
LOAD_ORG_NAME = "Load Test Org"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transactions", type=int, default=50_000)
    parser.add_argument("--accounts", type=int, default=25)
    parser.add_argument("--days", type=int, default=365, help="Spread occurred_at over N days")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete previous load-test org data before seeding",
    )
    return parser.parse_args()


def _delete_load_org(session) -> None:
    row = session.execute(
        text("SELECT id FROM organizations WHERE slug = :slug"),
        {"slug": "load-test-org"},
    ).first()
    if row is None:
        user = session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": LOAD_EMAIL},
        ).first()
        if user is not None:
            session.execute(text("DELETE FROM users WHERE id = :id"), {"id": user.id})
            session.commit()
        return

    org_id = row.id
    session.execute(
        text(
            """
            DELETE FROM goal_manual_progress
            WHERE goal_id IN (SELECT id FROM goals WHERE organization_id = :org_id)
            """
        ),
        {"org_id": org_id},
    )
    session.execute(
        text(
            """
            DELETE FROM goal_accounts
            WHERE goal_id IN (SELECT id FROM goals WHERE organization_id = :org_id)
            """
        ),
        {"org_id": org_id},
    )
    session.execute(
        text("DELETE FROM goals WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    session.execute(
        text(
            """
            DELETE FROM transaction_entries
            WHERE transaction_id IN (
                SELECT id FROM transactions WHERE organization_id = :org_id
            )
            """
        ),
        {"org_id": org_id},
    )
    session.execute(
        text("DELETE FROM transactions WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    session.execute(
        text("DELETE FROM categories WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    session.execute(
        text("DELETE FROM accounts WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    session.execute(
        text("DELETE FROM organization_memberships WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    session.execute(
        text("DELETE FROM organizations WHERE id = :org_id"),
        {"org_id": org_id},
    )
    session.execute(
        text("DELETE FROM users WHERE email = :email"),
        {"email": LOAD_EMAIL},
    )
    session.commit()


def _register(client: TestClient) -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": LOAD_EMAIL,
            "password": LOAD_PASSWORD,
            "display_name": "Load Tester",
            "organization_name": LOAD_ORG_NAME,
        },
    )
    if response.status_code == 201:
        token = response.json()["access_token"]
    else:
        # Already exists — login
        login = client.post(
            f"{AUTH}/login",
            data={"username": LOAD_EMAIL, "password": LOAD_PASSWORD},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    me = client.get(f"{AUTH}/me", headers=headers).json()
    return {"headers": headers, "org_id": org_id, "user_id": me["id"], "token": token}


def _category_ids(session, org_id: str) -> tuple[list[UUID], list[UUID]]:
    income = [
        row.id
        for row in session.execute(
            text(
                """
                SELECT id FROM categories
                WHERE organization_id = :org_id AND category_type = 'income' AND is_active
                """
            ),
            {"org_id": org_id},
        )
    ]
    expense = [
        row.id
        for row in session.execute(
            text(
                """
                SELECT id FROM categories
                WHERE organization_id = :org_id AND category_type = 'expense' AND is_active
                """
            ),
            {"org_id": org_id},
        )
    ]
    assert income and expense, "Expected seeded categories"
    return income, expense


def _create_accounts(session, org_id: str, count: int) -> list[UUID]:
    now = datetime.now(UTC)
    account_ids: list[UUID] = []
    rows = []
    for i in range(count):
        account_id = uuid4()
        account_ids.append(account_id)
        is_liability = i % 8 == 7
        opening = Decimal("-5000.00") if is_liability else Decimal("10000.00")
        rows.append(
            {
                "id": account_id,
                "organization_id": org_id,
                "name": f"Load Account {i + 1:02d}",
                "account_type": "credit_card" if is_liability else "checking",
                "classification": "liability" if is_liability else "asset",
                "currency": "MXN",
                "opening_balance": opening,
                "current_balance": opening,
                "institution_name": "Load Bank",
                "last_four": f"{i % 10000:04d}",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
                "archived_at": None,
            }
        )
    session.execute(
        text(
            """
            INSERT INTO accounts (
                id, organization_id, name, account_type, classification, currency,
                opening_balance, current_balance, institution_name, last_four,
                is_active, created_at, updated_at, archived_at
            ) VALUES (
                :id, :organization_id, :name, :account_type, :classification, :currency,
                :opening_balance, :current_balance, :institution_name, :last_four,
                :is_active, :created_at, :updated_at, :archived_at
            )
            """
        ),
        rows,
    )
    session.commit()
    return account_ids


def _bulk_transactions(
    session,
    *,
    org_id: str,
    user_id: str,
    account_ids: list[UUID],
    income_cats: list[UUID],
    expense_cats: list[UUID],
    count: int,
    days: int,
) -> None:
    rng = random.Random(42)
    now = datetime.now(UTC)
    start = now - timedelta(days=days)
    batch_size = 2_000
    inserted = 0
    balances = {account_id: Decimal("0.00") for account_id in account_ids}

    while inserted < count:
        n = min(batch_size, count - inserted)
        tx_rows = []
        entry_rows = []
        for _ in range(n):
            tx_id = uuid4()
            is_income = rng.random() < 0.45
            account_id = account_ids[rng.randrange(len(account_ids))]
            amount = Decimal(str(round(rng.uniform(50, 5_000), 2)))
            signed = amount if is_income else -amount
            balances[account_id] += signed
            occurred = start + timedelta(
                seconds=rng.randint(0, max(days * 24 * 3600 - 1, 1))
            )
            tx_rows.append(
                {
                    "id": tx_id,
                    "organization_id": org_id,
                    "transaction_type": "income" if is_income else "expense",
                    "description": f"Load tx {inserted + len(tx_rows) + 1}",
                    "category_id": (
                        income_cats[rng.randrange(len(income_cats))]
                        if is_income
                        else expense_cats[rng.randrange(len(expense_cats))]
                    ),
                    "occurred_at": occurred,
                    "notes": None,
                    "status": "posted",
                    "created_by_user_id": user_id,
                    "updated_by_user_id": user_id,
                    "voided_by_user_id": None,
                    "created_at": now,
                    "updated_at": now,
                    "voided_at": None,
                }
            )
            entry_rows.append(
                {
                    "id": uuid4(),
                    "transaction_id": tx_id,
                    "account_id": account_id,
                    "amount": signed,
                    "currency": "MXN",
                    "created_at": now,
                }
            )
        session.execute(
            text(
                """
                INSERT INTO transactions (
                    id, organization_id, transaction_type, description, category_id,
                    occurred_at, notes, status, created_by_user_id, updated_by_user_id,
                    voided_by_user_id, created_at, updated_at, voided_at
                ) VALUES (
                    :id, :organization_id, :transaction_type, :description, :category_id,
                    :occurred_at, :notes, :status, :created_by_user_id, :updated_by_user_id,
                    :voided_by_user_id, :created_at, :updated_at, :voided_at
                )
                """
            ),
            tx_rows,
        )
        session.execute(
            text(
                """
                INSERT INTO transaction_entries (
                    id, transaction_id, account_id, amount, currency, created_at
                ) VALUES (
                    :id, :transaction_id, :account_id, :amount, :currency, :created_at
                )
                """
            ),
            entry_rows,
        )
        session.commit()
        inserted += n
        print(f"  inserted {inserted}/{count} transactions", flush=True)

    # Apply deltas on top of opening balances
    for account_id, delta in balances.items():
        session.execute(
            text(
                """
                UPDATE accounts
                SET current_balance = opening_balance + :delta, updated_at = :now
                WHERE id = :id
                """
            ),
            {"delta": delta, "now": now, "id": account_id},
        )
    session.commit()


def _seed_goals(session, org_id: str, account_ids: list[UUID]) -> None:
    now = datetime.now(UTC)
    linked_id = uuid4()
    manual_id = uuid4()
    nw_id = uuid4()
    goals = [
        {
            "id": linked_id,
            "organization_id": org_id,
            "name": "Fondo emergencia",
            "target_amount": Decimal("200000.00"),
            "currency": "MXN",
            "target_date": None,
            "strategy": "linked_accounts",
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
            "archived_at": None,
        },
        {
            "id": manual_id,
            "organization_id": org_id,
            "name": "Viaje Japón",
            "target_amount": Decimal("80000.00"),
            "currency": "MXN",
            "target_date": None,
            "strategy": "manual",
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
            "archived_at": None,
        },
        {
            "id": nw_id,
            "organization_id": org_id,
            "name": "FIRE",
            "target_amount": Decimal("5000000.00"),
            "currency": "MXN",
            "target_date": None,
            "strategy": "net_worth_percentage",
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
            "archived_at": None,
        },
    ]
    session.execute(
        text(
            """
            INSERT INTO goals (
                id, organization_id, name, target_amount, currency, target_date,
                strategy, status, created_at, updated_at, completed_at, archived_at
            ) VALUES (
                :id, :organization_id, :name, :target_amount, :currency, :target_date,
                :strategy, :status, :created_at, :updated_at, :completed_at, :archived_at
            )
            """
        ),
        goals,
    )
    session.execute(
        text(
            "INSERT INTO goal_accounts (goal_id, account_id) VALUES (:goal_id, :account_id)"
        ),
        {"goal_id": linked_id, "account_id": account_ids[0]},
    )
    session.execute(
        text(
            """
            INSERT INTO goal_manual_progress (goal_id, current_amount, updated_at)
            VALUES (:goal_id, :current_amount, :updated_at)
            """
        ),
        {
            "goal_id": manual_id,
            "current_amount": Decimal("35000.00"),
            "updated_at": now,
        },
    )
    session.commit()


def main() -> None:
    args = _parse_args()
    started = time.perf_counter()
    print(f"Seeding load org with {args.transactions} transactions…")

    with SessionLocal() as session:
        if args.reset:
            print("Resetting previous load-test data…")
            _delete_load_org(session)

    with TestClient(app) as client:
        user = _register(client)

    with SessionLocal() as session:
        existing = session.execute(
            text(
                "SELECT COUNT(*) FROM transactions WHERE organization_id = :org_id"
            ),
            {"org_id": user["org_id"]},
        ).scalar_one()
        if existing and not args.reset:
            print(
                f"Org already has {existing} transactions. "
                "Re-run with --reset to rebuild."
            )
            print(f"email={LOAD_EMAIL}")
            print(f"password={LOAD_PASSWORD}")
            print(f"organization_id={user['org_id']}")
            return

        if existing and args.reset:
            # register after reset already emptied data
            pass

        income_cats, expense_cats = _category_ids(session, user["org_id"])
        print(f"Creating {args.accounts} accounts…")
        account_ids = _create_accounts(session, user["org_id"], args.accounts)
        print("Bulk inserting transactions…")
        _bulk_transactions(
            session,
            org_id=user["org_id"],
            user_id=user["user_id"],
            account_ids=account_ids,
            income_cats=income_cats,
            expense_cats=expense_cats,
            count=args.transactions,
            days=args.days,
        )
        print("Seeding sample goals…")
        _seed_goals(session, user["org_id"], account_ids)

    elapsed = round(time.perf_counter() - started, 2)
    print(f"Done in {elapsed}s")
    print(f"email={LOAD_EMAIL}")
    print(f"password={LOAD_PASSWORD}")
    print(f"organization_id={user['org_id']}")


if __name__ == "__main__":
    main()
