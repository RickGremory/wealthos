#!/usr/bin/env python3
"""Export / import personal WealthOS data (local only, not for git).

Use this to protect real captured data while the app is still in flux.
Snapshots land under ``local/personal-snapshots/`` (gitignored).

Examples (from ``backend/``, Postgres up):

  # Export by user id or email
  uv run python scripts/personal_snapshot.py export \\
    --user-id 08817a09-cb04-4c15-a3a2-a8ceb8d68ce4

  uv run python scripts/personal_snapshot.py export \\
    --email ricardo.balamc@gmail.com

  # Re-load the latest snapshot for that email slug
  uv run python scripts/personal_snapshot.py import --latest \\
    --email ricardo.balamc@gmail.com

  # Or point at a specific folder
  uv run python scripts/personal_snapshot.py import \\
    ../local/personal-snapshots/ricardo-balamc-gmail-com/2026-08-02T033000Z

Notes:
  - Includes password_hash so you can log in after restore (local secret).
  - Preserves UUIDs so relationships stay intact.
  - Idempotent upsert (safe to re-run).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
SNAPSHOT_ROOT = REPO_ROOT / "local" / "personal-snapshots"

sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("DB_ECHO", "false")

# Child tables without organization_id (exported via parent FK join).
# Tables that already have organization_id are covered by the org-scoped dump.
CHILD_SPECS: list[tuple[str, str, str]] = [
    # (child_table, fk_column, parent_table)
    ("transaction_entries", "transaction_id", "transactions"),
    ("goal_accounts", "goal_id", "goals"),
    ("goal_manual_progress", "goal_id", "goals"),
    ("cash_plan_accounts", "cash_plan_id", "cash_plans"),
]

# Import order (FK-safe). Unknown org-scoped tables append after these.
IMPORT_ORDER = [
    "users",
    "organizations",
    "organization_memberships",
    "accounts",
    "categories",
    "goals",
    "goal_accounts",
    "goal_manual_progress",
    "transactions",
    "transaction_entries",
    "planned_cash_flows",
    "planning_settings",
    "legal_consents",
    "timeline_events",
    "debts",
    "debt_payments",
    "budgets",
    "budget_allocations",
    "budget_allocation_matches",
    "cash_plans",
    "cash_plan_accounts",
    "cash_plan_items",
    "cash_plan_item_matches",
    "recurring_rules",
    "recurring_rule_versions",
    "recurring_rule_pauses",
    "recurring_occurrence_exceptions",
    "recurring_occurrence_settlements",
]


def _load_database_url() -> str:
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is not set (check backend/.env)")
    return url


def _engine() -> Engine:
    return create_engine(_load_database_url())


def _json_default(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, memoryview):
        return bytes(value).hex()
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).hex()
    raise TypeError(f"Not JSON serializable: {type(value)!r}")


def _slug_email(email: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", email.lower()).strip("-")


def _table_names(engine: Engine) -> set[str]:
    return set(inspect(engine).get_table_names())


def _pk_columns(engine: Engine, table: str) -> list[str]:
    pk = inspect(engine).get_pk_constraint(table)
    return list(pk.get("constrained_columns") or [])


def _column_names(engine: Engine, table: str) -> list[str]:
    return [col["name"] for col in inspect(engine).get_columns(table)]


def _fetch_dicts(engine: Engine, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return [dict(row) for row in rows]


def _fetch_by_ids(engine: Engine, table: str, id_column: str, ids: list[str]) -> list[dict[str, Any]]:
    if not ids:
        return []
    binds = {f"id{i}": ids[i] for i in range(len(ids))}
    placeholders = ", ".join(f":id{i}" for i in range(len(ids)))
    return _fetch_dicts(
        engine,
        f'SELECT * FROM "{table}" WHERE "{id_column}" IN ({placeholders})',
        binds,
    )


def _org_scoped_tables(engine: Engine) -> list[str]:
    names = []
    for table in sorted(_table_names(engine)):
        if "organization_id" in _column_names(engine, table):
            names.append(table)
    return names


def resolve_user(engine: Engine, *, user_id: str | None, email: str | None) -> dict[str, Any]:
    if user_id:
        rows = _fetch_dicts(engine, "SELECT * FROM users WHERE id = :id", {"id": user_id})
    elif email:
        rows = _fetch_dicts(
            engine,
            "SELECT * FROM users WHERE lower(email) = lower(:email)",
            {"email": email},
        )
    else:
        raise SystemExit("Provide --user-id or --email")
    if not rows:
        raise SystemExit("User not found")
    return rows[0]


def export_snapshot(engine: Engine, user: dict[str, Any], out_dir: Path) -> Path:
    user_id = str(user["id"])
    memberships = _fetch_dicts(
        engine,
        "SELECT * FROM organization_memberships WHERE user_id = :uid",
        {"uid": user_id},
    )
    org_ids = [str(m["organization_id"]) for m in memberships]
    if not org_ids:
        raise SystemExit("User has no organizations to export")

    orgs = _fetch_by_ids(engine, "organizations", "id", org_ids)

    tables: dict[str, list[dict[str, Any]]] = {
        "users": [user],
        "organizations": orgs,
        "organization_memberships": memberships,
    }

    existing = _table_names(engine)
    for table in _org_scoped_tables(engine):
        if table in {"organization_memberships"}:
            continue
        rows = _fetch_by_ids(engine, table, "organization_id", org_ids)
        if rows:
            tables[table] = rows

    for child, fk_col, parent in CHILD_SPECS:
        if child not in existing or parent not in existing:
            continue
        if parent not in tables or not tables[parent]:
            continue
        parent_ids = [str(row["id"]) for row in tables[parent] if "id" in row]
        rows = _fetch_by_ids(engine, child, fk_col, parent_ids)
        if rows:
            tables[child] = rows

    # Categories: parents before children helps humans reading the file.
    if "categories" in tables:
        tables["categories"].sort(
            key=lambda row: (row.get("parent_id") is not None, str(row.get("parent_id") or ""))
        )

    counts = {name: len(rows) for name, rows in tables.items()}
    stamped = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    target = out_dir / stamped
    target.mkdir(parents=True, exist_ok=True)

    payload = {
        "format": "wealthos.personal_snapshot.v1",
        "exported_at": datetime.now(UTC).isoformat(),
        "user": {
            "id": user_id,
            "email": user["email"],
            "display_name": user.get("display_name"),
        },
        "organization_ids": org_ids,
        "counts": counts,
        "tables": tables,
    }
    data_path = target / "snapshot.json"
    data_path.write_text(json.dumps(payload, indent=2, default=_json_default) + "\n")

    latest = out_dir / "latest"
    if latest.is_symlink() or latest.exists():
        latest.unlink()
    try:
        latest.symlink_to(target.name)
    except OSError:
        # Fallback when symlinks are restricted: copy pointer file.
        (out_dir / "latest.txt").write_text(str(target) + "\n")

    manifest = {
        "exported_at": payload["exported_at"],
        "user_id": user_id,
        "user_email": user["email"],
        "organization_ids": org_ids,
        "counts": counts,
        "path": str(data_path),
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return target


def _coerce_value(value: Any) -> Any:
    if isinstance(value, dict | list):
        # JSON/JSONB columns come back as dict/list from export.
        return json.dumps(value)
    return value


def _upsert_rows(engine: Engine, table: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    pk = _pk_columns(engine, table)
    if not pk:
        raise RuntimeError(f"Table {table} has no primary key; cannot upsert")
    cols = [c for c in _column_names(engine, table) if c in rows[0]]
    col_list = ", ".join(f'"{c}"' for c in cols)
    placeholders = ", ".join(f":{c}" for c in cols)
    conflict = ", ".join(f'"{c}"' for c in pk)
    non_pk = [c for c in cols if c not in pk]
    if non_pk:
        set_clause = ", ".join(f'"{c}" = EXCLUDED."{c}"' for c in non_pk)
        sql = (
            f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders}) '
            f"ON CONFLICT ({conflict}) DO UPDATE SET {set_clause}"
        )
    else:
        sql = (
            f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders}) '
            f"ON CONFLICT ({conflict}) DO NOTHING"
        )

    # Categories: insert roots first to satisfy self-FK.
    ordered = rows
    if table == "categories":
        ordered = sorted(rows, key=lambda r: (r.get("parent_id") is not None, str(r.get("id"))))

    with engine.begin() as conn:
        for row in ordered:
            params = {c: _coerce_value(row.get(c)) for c in cols}
            conn.execute(text(sql), params)
    return len(rows)


def import_snapshot(engine: Engine, snapshot_dir: Path) -> None:
    data_path = snapshot_dir / "snapshot.json"
    if not data_path.exists():
        raise SystemExit(f"Missing snapshot.json in {snapshot_dir}")
    payload = json.loads(data_path.read_text())
    if payload.get("format") != "wealthos.personal_snapshot.v1":
        raise SystemExit(f"Unsupported snapshot format: {payload.get('format')}")

    tables: dict[str, list[dict[str, Any]]] = payload["tables"]
    existing = _table_names(engine)
    ordered = [t for t in IMPORT_ORDER if t in tables and t in existing]
    ordered.extend(sorted(t for t in tables if t not in ordered and t in existing))

    print(f"Importing snapshot for {payload['user']['email']} from {snapshot_dir}")
    for table in ordered:
        count = _upsert_rows(engine, table, tables[table])
        print(f"  ✓ {table}: {count}")
    print("Done. You can log in with the same email/password as before the export.")


def _resolve_latest(email: str | None) -> Path:
    if not email:
        raise SystemExit("--latest requires --email")
    folder = SNAPSHOT_ROOT / _slug_email(email)
    if not folder.exists():
        raise SystemExit(f"No snapshots under {folder}")
    latest = folder / "latest"
    if latest.is_symlink():
        return (folder / Path(os.readlink(latest))).resolve()
    latest_txt = folder / "latest.txt"
    if latest_txt.exists():
        return Path(latest_txt.read_text().strip())
    stamped = sorted(
        [p for p in folder.iterdir() if p.is_dir() and (p / "snapshot.json").exists()],
        key=lambda p: p.name,
    )
    if not stamped:
        raise SystemExit(f"No snapshot.json found under {folder}")
    return stamped[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    export_p = sub.add_parser("export", help="Write a personal snapshot under local/personal-snapshots/")
    export_p.add_argument("--user-id", help="User UUID to export")
    export_p.add_argument("--email", help="User email to export")
    export_p.add_argument(
        "--out",
        type=Path,
        help="Optional output directory (defaults to local/personal-snapshots/<email-slug>/)",
    )

    import_p = sub.add_parser("import", help="Upsert a snapshot back into the local database")
    import_p.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="Snapshot directory containing snapshot.json",
    )
    import_p.add_argument("--latest", action="store_true", help="Import latest snapshot for --email")
    import_p.add_argument("--email", help="Used with --latest to locate the snapshot folder")
    import_p.add_argument("--user-id", help="Optional; prefer --email with --latest")

    args = parser.parse_args()
    engine = _engine()

    if args.command == "export":
        user = resolve_user(engine, user_id=args.user_id, email=args.email)
        out_dir = args.out or (SNAPSHOT_ROOT / _slug_email(str(user["email"])))
        out_dir.mkdir(parents=True, exist_ok=True)
        target = export_snapshot(engine, user, out_dir)
        print(f"✓ Snapshot written to {target}")
        print(f"  email={user['email']}")
        print(f"  orgs={json.loads((target / 'manifest.json').read_text())['organization_ids']}")
        print(f"  counts={json.loads((target / 'manifest.json').read_text())['counts']}")
        print("  (folder is gitignored via local/)")
        return

    if args.command == "import":
        if args.latest:
            snapshot_dir = _resolve_latest(args.email)
        elif args.path:
            snapshot_dir = args.path
        else:
            raise SystemExit("Provide a snapshot path or --latest --email …")
        import_snapshot(engine, snapshot_dir)
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
