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

### After optimizations (query rewrite + `0011` indexes + ANALYZE)

SQL `Execution Time` (`perf/explain/latest/SUMMARY.txt`):

| Query | Before | After |
|-------|--------|-------|
| cash_flow_monthly | ~50 ms | ~36 ms |
| period_cash_flow_summary | ~20 ms | ~20 ms |
| spending_by_category | ~32 ms | ~30 ms |
| average_daily_savings_90d | unstable (nested-loop blowups) | ~12 ms |
| recent_transactions | ~0.04 ms | ~0.1 ms |
| net_worth_mxn | ~0.03 ms | ~0.02 ms |

HTTP p50 (`BENCHMARK.txt`): summary ~45 ms, cash-flow ~30 ms, spending ~33 ms,
goals ~22–23 ms.

### Changes shipped

1. **`average_daily_savings`** starts from `transactions` (uses org/status/time indexes).
2. **`GoalProgressService`** request-scoped cache for manual/balances/net-worth/savings.
3. **`0011_stabilize_query_indexes`**: partial cash-flow index + entry covering indexes.
4. **Seed** runs `ANALYZE` after bulk insert so the planner stays honest.

### Remaining notes

- At 50k rows the planner may still prefer seq/hash plans for full-year cash-flow;
  re-check at 200k–500k.
- Dashboard `summary` still embeds goals counts (extra work vs pure balances).
- Prefer re-seeding with `make perf-seed` after large data loads so `ANALYZE` runs.
