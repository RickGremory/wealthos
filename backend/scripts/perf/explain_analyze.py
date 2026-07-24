#!/usr/bin/env python3
"""Run EXPLAIN (ANALYZE, BUFFERS) for the heaviest Dashboard/Goals SQL.

Usage (from backend/):
  uv run python scripts/perf/explain_analyze.py
  uv run python scripts/perf/explain_analyze.py --org-id <uuid>

Writes plans to backend/perf/explain/latest/
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

os.environ.setdefault("DB_ECHO", "false")
os.environ.setdefault("DEBUG", "false")

from wealthos.core.database import SessionLocal  # noqa: E402

OUT_DIR = ROOT / "perf" / "explain" / "latest"
LOAD_SLUG = "load-test-org"


QUERIES: dict[str, str] = {
    "cash_flow_monthly": """
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
  te.currency,
  date_trunc(
    'month',
    timezone('America/Mexico_City', t.occurred_at)
  ) AS bucket,
  COALESCE(
    SUM(CASE WHEN t.transaction_type = 'income' THEN te.amount ELSE 0 END),
    0
  ) AS income,
  COALESCE(
    SUM(
      CASE WHEN t.transaction_type = 'expense' THEN ABS(te.amount) ELSE 0 END
    ),
    0
  ) AS expenses
FROM transactions t
JOIN transaction_entries te ON te.transaction_id = t.id
WHERE t.organization_id = :org_id
  AND t.status = 'posted'
  AND t.transaction_type IN ('income', 'expense')
  AND t.occurred_at >= :start_at
  AND t.occurred_at < :end_at
GROUP BY te.currency, bucket
ORDER BY te.currency, bucket;
""",
    "period_cash_flow_summary": """
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
  te.currency,
  COALESCE(
    SUM(CASE WHEN t.transaction_type = 'income' THEN te.amount ELSE 0 END),
    0
  ) AS income,
  COALESCE(
    SUM(
      CASE WHEN t.transaction_type = 'expense' THEN ABS(te.amount) ELSE 0 END
    ),
    0
  ) AS expenses
FROM transactions t
JOIN transaction_entries te ON te.transaction_id = t.id
WHERE t.organization_id = :org_id
  AND t.status = 'posted'
  AND t.transaction_type IN ('income', 'expense')
  AND t.occurred_at >= :start_at
  AND t.occurred_at < :end_at
GROUP BY te.currency;
""",
    "spending_by_category": """
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
  te.currency,
  c.id AS category_id,
  c.name AS category_name,
  c.parent_id,
  COALESCE(SUM(ABS(te.amount)), 0) AS amount,
  COUNT(DISTINCT t.id) AS tx_count
FROM transactions t
JOIN transaction_entries te ON te.transaction_id = t.id
JOIN categories c ON c.id = t.category_id
WHERE t.organization_id = :org_id
  AND t.status = 'posted'
  AND t.transaction_type = 'expense'
  AND t.occurred_at >= :start_at
  AND t.occurred_at < :end_at
GROUP BY te.currency, c.id, c.name, c.parent_id;
""",
    "recent_transactions": """
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT t.id, t.occurred_at, t.created_at
FROM transactions t
WHERE t.organization_id = :org_id
ORDER BY t.occurred_at DESC, t.created_at DESC
LIMIT 20;
""",
    "average_daily_savings_90d": """
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT COALESCE(SUM(te.amount), 0) AS total
FROM transactions t
JOIN transaction_entries te ON te.transaction_id = t.id
JOIN accounts a ON a.id = te.account_id
WHERE t.organization_id = :org_id
  AND t.status = 'posted'
  AND t.occurred_at >= :start_90d
  AND te.currency = 'MXN'
  AND a.currency = 'MXN';
""",
    "net_worth_mxn": """
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
  COALESCE(
    SUM(
      CASE WHEN a.classification = 'asset' THEN a.current_balance ELSE 0 END
    ),
    0
  )
  - COALESCE(
    SUM(
      CASE
        WHEN a.classification = 'liability' THEN ABS(a.current_balance)
        ELSE 0
      END
    ),
    0
  ) AS net_worth
FROM accounts a
WHERE a.organization_id = :org_id
  AND a.currency = 'MXN'
  AND a.is_active IS TRUE;
""",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--org-id", default="")
    return parser.parse_args()


def _resolve_org_id(session, explicit: str) -> str:
    if explicit:
        return explicit
    row = session.execute(
        text("SELECT id FROM organizations WHERE slug = :slug"),
        {"slug": LOAD_SLUG},
    ).first()
    if row is None:
        raise SystemExit(
            "Load-test organization not found. Run scripts/perf/seed_load.py first."
        )
    return str(row.id)


def main() -> None:
    args = _parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC)
    start_at = datetime(now.year, 1, 1, tzinfo=UTC)
    end_at = datetime(now.year + 1, 1, 1, tzinfo=UTC)
    start_90d = now - timedelta(days=90)

    with SessionLocal() as session:
        org_id = _resolve_org_id(session, args.org_id)
        params = {
            "org_id": org_id,
            "start_at": start_at,
            "end_at": end_at,
            "start_90d": start_90d,
        }
        summary_lines = [
            f"organization_id={org_id}",
            f"generated_at={now.isoformat()}",
            "",
        ]
        print(f"Writing EXPLAIN plans for org {org_id} → {OUT_DIR}")
        for name, sql in QUERIES.items():
            rows = session.execute(text(sql), params).all()
            plan = "\n".join(row[0] for row in rows)
            out_file = OUT_DIR / f"{name}.txt"
            out_file.write_text(plan + "\n", encoding="utf-8")
            # Extract Execution Time line if present
            exec_line = next(
                (line for line in plan.splitlines() if "Execution Time" in line),
                "Execution Time: n/a",
            )
            summary_lines.append(f"{name}: {exec_line.strip()}")
            print(f"  {name}: {exec_line.strip()}")

        (OUT_DIR / "SUMMARY.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
