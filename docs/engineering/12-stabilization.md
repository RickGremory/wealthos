# 12 — Stabilization milestone

After Accounts → Transactions → Dashboard → Goals, WealthOS has a usable
financial core. Before Debts / Taxes / Budgets / AI, we stabilize under load.

## Goals

1. Seed tens of thousands of transactions and measure HTTP latency.
2. Capture `EXPLAIN (ANALYZE, BUFFERS)` for the heaviest Dashboard/Goals SQL.
3. Emit structured timing logs for critical requests and usecases.

## How to run

From `backend/`:

```bash
make migrate
make perf-seed      # 50k txs by default (--reset)
make perf-explain   # writes perf/explain/latest/*.txt
make perf-bench     # p50/p95 for dashboard + goals endpoints
```

Or directly:

```bash
uv run python scripts/perf/seed_load.py --reset --transactions 50000
uv run python scripts/perf/explain_analyze.py
uv run python scripts/perf/benchmark_http.py --iterations 10
```

## Observability

- Setting: `REQUEST_TIMING_ENABLED` (default `true`)
- Middleware logs `http_request` with `duration_ms`, `path`, `status_code`, `request_id`
- Usecases log `usecase_timing` for:
  - `dashboard.summary`
  - `dashboard.cash_flow`
  - `dashboard.spending_by_category`
  - `dashboard.goals_summary`
  - `goals.progress`
- Timing is suppressed under pytest (`PYTEST_CURRENT_TEST`)

## Known hotspots to watch

| Query | Why |
|-------|-----|
| cash-flow with `date_trunc` + timezone | Heaviest dashboard aggregation |
| spending-by-category | Join + group + Python root merge |
| `average_daily_savings` (90d) | Called per linked/net-worth goal |
| goals dashboard summary | N × progress calculate (N+1 risk) |

Index baseline: migrations `0008`, `0009`, `0010`. New indexes only after EXPLAIN
shows sequential scans or poor index usage on seeded data.

## Acceptance for this milestone

- [x] Seed ≥ 50k posted transactions for one org
- [x] EXPLAIN plans captured for cash-flow, spending, recent txs, avg savings, net worth
- [x] Benchmark table with p50/p95 for dashboard + goals endpoints
- [x] Structured timing present in non-test runs
- [x] Document any index follow-ups discovered from plans

## Baseline (2026-07-23, 50k txs / 25 accounts)

SQL `Execution Time` (`perf/explain/latest/SUMMARY.txt`):

| Query | Time |
|-------|------|
| cash_flow_monthly | ~50 ms |
| period_cash_flow_summary | ~20 ms |
| spending_by_category | ~32 ms |
| average_daily_savings_90d | ~13 ms |
| recent_transactions | ~0.04 ms |
| net_worth_mxn | ~0.03 ms |

HTTP p50 (TestClient, `BENCHMARK.txt`): summary ~45 ms, cash-flow ~32 ms,
spending ~34 ms, goals ~22 ms.

### Follow-ups from EXPLAIN

1. **cash_flow / period summary** — planner chose `Seq Scan` on `transactions`
   and `transaction_entries` at 50k rows. Indexes from `0009` exist; at this
   size seq scan can be cheaper. Re-check at 200k–500k before adding indexes.
2. **average_daily_savings** — still `Seq Scan` on all entries then joins.
   Prefer rewriting the query to start from `transactions` filtered by
   `(organization_id, status, occurred_at)` then join entries/accounts.
3. **goals dashboard** — N progress calculations (linked/net-worth each hit
   savings SQL). Batch or cache avg-daily-savings per org/currency when many
   goals exist.
4. **recent_transactions** — uses
   `ix_transactions_organization_id_occurred_created` correctly (keep).
