#!/usr/bin/env python3
"""Ensure a stable local demo account exists (idempotent).

Usage (from backend/, with Postgres up):

  uv run python scripts/seed_demo.py
  uv run python scripts/seed_demo.py --reset-password
  uv run python scripts/seed_demo.py --with-sample-data

Credentials (fixed — do not change casually):

  Email:    demo@wealthos.test
  Password: WealthOS-2026-Segura
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

os.environ.setdefault("DB_ECHO", "false")
os.environ.setdefault("DEBUG", "false")

from wealthos.core.database import SessionLocal  # noqa: E402
from wealthos.main import app  # noqa: E402
from wealthos.modules.identity.infrastructure.security.pwdlib_password_hasher import (  # noqa: E402
    PwdlibPasswordHasher,
)

AUTH = "/api/v1/auth"
ME = "/api/v1/me"
ORG = "/api/v1/organizations"

DEMO_EMAIL = "demo@wealthos.test"
DEMO_PASSWORD = "WealthOS-2026-Segura"
DEMO_DISPLAY_NAME = "Demo WealthOS"
DEMO_ORG_NAME = "Finanzas personales"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset-password",
        action="store_true",
        help="Force-reset the demo password hash even if login already works",
    )
    parser.add_argument(
        "--with-sample-data",
        action="store_true",
        help="Ensure a checking account, sample income/expense, and a goal exist",
    )
    return parser.parse_args()


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _login(client: TestClient) -> str | None:
    response = client.post(
        f"{AUTH}/login",
        data={"username": DEMO_EMAIL, "password": DEMO_PASSWORD},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def _ensure_password_hash(*, reset: bool) -> None:
    hasher = PwdlibPasswordHasher()
    with SessionLocal() as session:
        row = session.execute(
            text("SELECT id, password_hash FROM users WHERE email = :email"),
            {"email": DEMO_EMAIL},
        ).one_or_none()
        if row is None:
            return
        user_id, current_hash = row
        if reset or not hasher.verify(DEMO_PASSWORD, current_hash):
            session.execute(
                text(
                    "UPDATE users SET password_hash = :hash, display_name = :name, "
                    "updated_at = :now WHERE id = :id"
                ),
                {
                    "hash": hasher.hash(DEMO_PASSWORD),
                    "name": DEMO_DISPLAY_NAME,
                    "now": datetime.now(UTC),
                    "id": user_id,
                },
            )
            session.commit()
            print(f"✓ Password reset for {DEMO_EMAIL}")


def _register(client: TestClient) -> str:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD,
            "display_name": DEMO_DISPLAY_NAME,
            "organization_name": DEMO_ORG_NAME,
            "currency": "MXN",
            "timezone": "America/Merida",
            "locale": "es-MX",
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
    if response.status_code == 201:
        print(f"✓ Created demo user {DEMO_EMAIL}")
        return response.json()["access_token"]
    raise SystemExit(f"Could not register demo user: {response.status_code} {response.text}")


def _org_id(client: TestClient, token: str) -> str:
    orgs = client.get(f"{ME}/organizations", headers=_headers(token))
    orgs.raise_for_status()
    items = orgs.json()["items"]
    if not items:
        raise SystemExit("Demo user has no organizations")
    return items[0]["id"]


def _ensure_sample_data(client: TestClient, token: str, org_id: str) -> None:
    headers = _headers(token)
    accounts = client.get(f"{ORG}/{org_id}/accounts", headers=headers)
    accounts.raise_for_status()
    items = accounts.json().get("items") or []

    if not items:
        created = client.post(
            f"{ORG}/{org_id}/accounts",
            headers=headers,
            json={
                "name": "HSBC principal",
                "account_type": "checking",
                "currency": "MXN",
                "opening_balance": "50000.00",
                "opening_balance_date": "2026-07-01",
                "institution_name": "HSBC",
                "last_four": "4821",
            },
        )
        created.raise_for_status()
        account_id = created.json()["id"]
        print("✓ Created demo checking account")
    else:
        account_id = items[0]["id"]
        print("· Demo account already present")

    categories = client.get(
        f"{ORG}/{org_id}/categories",
        headers=headers,
        params={"include_archived": "false", "tree": "true"},
    )
    categories.raise_for_status()
    cat_payload = categories.json()
    cat_items = cat_payload.get("items") or cat_payload.get("tree") or []

    def _flatten(nodes: list, acc: list | None = None) -> list:
        out = acc if acc is not None else []
        for node in nodes:
            out.append(node)
            children = node.get("children") or []
            if children:
                _flatten(children, out)
        return out

    flat = _flatten(cat_items if isinstance(cat_items, list) else [])
    income_cat = next((c for c in flat if c.get("category_type") == "income"), None)
    expense_cat = next((c for c in flat if c.get("category_type") == "expense"), None)

    txs = client.get(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        params={"limit": 50},
    )
    posted_ops = 0
    if txs.status_code == 200:
        posted_ops = sum(
            1
            for item in (txs.json().get("items") or [])
            if item.get("transaction_type") in {"income", "expense"}
        )

    if posted_ops == 0 and income_cat and expense_cat:
        today = date.today()
        income = client.post(
            f"{ORG}/{org_id}/transactions",
            headers={**headers, "Idempotency-Key": str(uuid4())},
            json={
                "transaction_type": "income",
                "account_id": account_id,
                "category_id": income_cat["id"],
                "amount": "45000.00",
                "description": "Cobro cliente — demo",
                "occurred_at": datetime(
                    today.year,
                    today.month,
                    max(1, today.day - 3),
                    10,
                    0,
                    tzinfo=UTC,
                ).isoformat(),
            },
        )
        if income.status_code not in (200, 201):
            print(f"· Skipping sample income ({income.status_code}): {income.text[:120]}")
        else:
            print("✓ Sample income posted")

        expense = client.post(
            f"{ORG}/{org_id}/transactions",
            headers={**headers, "Idempotency-Key": str(uuid4())},
            json={
                "transaction_type": "expense",
                "account_id": account_id,
                "category_id": expense_cat["id"],
                "amount": "1850.00",
                "description": "Software / suscripciones — demo",
                "occurred_at": datetime(
                    today.year,
                    today.month,
                    max(1, today.day - 1),
                    16,
                    30,
                    tzinfo=UTC,
                ).isoformat(),
            },
        )
        if expense.status_code not in (200, 201):
            print(f"· Skipping sample expense ({expense.status_code}): {expense.text[:120]}")
        else:
            print("✓ Sample expense posted")
    elif posted_ops > 0:
        print("· Demo income/expense already present")
    else:
        print("· Categories unavailable — skipping sample movements")

    goals = client.get(f"{ORG}/{org_id}/goals", headers=headers)
    if goals.status_code == 200 and int(goals.json().get("total") or 0) == 0:
        goal = client.post(
            f"{ORG}/{org_id}/goals",
            headers=headers,
            json={
                "name": "Fondo de emergencia",
                "target_amount": "90000.00",
                "currency": "MXN",
                "strategy": "linked_accounts",
                "target_date": (date.today() + timedelta(days=365)).isoformat(),
                "linked_account_ids": [account_id],
            },
        )
        if goal.status_code in (200, 201):
            print("✓ Demo goal created")
        else:
            print(f"· Skipping demo goal ({goal.status_code})")
    else:
        print("· Demo goals already present")


def main() -> None:
    args = _parse_args()
    print("Seeding WealthOS demo account…")

    with TestClient(app) as client:
        token = _login(client)
        if token is None:
            # User missing or password drifted — fix hash if row exists, else register.
            _ensure_password_hash(reset=True)
            token = _login(client)
            if token is None:
                token = _register(client)
            else:
                print(f"✓ Demo login restored for {DEMO_EMAIL}")
        else:
            print(f"✓ Demo login OK for {DEMO_EMAIL}")
            if args.reset_password:
                _ensure_password_hash(reset=True)
                token = _login(client)
                if token is None:
                    raise SystemExit("Password reset failed — login still invalid")

        if args.with_sample_data:
            org_id = _org_id(client, token)
            _ensure_sample_data(client, token, org_id)

    print()
    print("Demo credentials (stable):")
    print(f"  Email:    {DEMO_EMAIL}")
    print(f"  Password: {DEMO_PASSWORD}")
    print()
    print("Tip: after docker/DB resets, run:")
    print("  cd backend && uv run python scripts/seed_demo.py --with-sample-data")


if __name__ == "__main__":
    main()
