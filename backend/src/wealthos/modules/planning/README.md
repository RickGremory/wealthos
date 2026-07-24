# Planning

## Purpose

Operational **budgets** (period income/expense envelopes) and **cash plans** (dated liquidity projections) so organizations can plan spend, track pace, and anticipate shortfalls.

## Responsibilities

- Budget lifecycle: draft → active → close / archive, with typed allocations (income, expense, savings, tax reserve, debt payment, goal contribution).
- Cash plan lifecycle with dated items, transaction matching, scenario projections, and alerts.
- Cross-module suggestions (debts payment days, tax balance due) and a planning summary including `safe_to_spend` (estimate, not advice).

## Public API

Mounted under `/api/v1/organizations/{organization_id}/...` (tag **Planning**). Not registered via `MODULES`.

### Budgets

| Method | Path |
|--------|------|
| POST | `/budgets` |
| GET | `/budgets` |
| GET | `/budgets/{budget_id}` |
| PATCH | `/budgets/{budget_id}` |
| POST | `/budgets/{budget_id}/activate` |
| POST | `/budgets/{budget_id}/close` |
| POST | `/budgets/{budget_id}/archive` |
| POST | `/budgets/{budget_id}/allocations` |
| PATCH | `/budgets/{budget_id}/allocations/{allocation_id}` |
| DELETE | `/budgets/{budget_id}/allocations/{allocation_id}` |
| POST | `/budgets/{budget_id}/allocations/{allocation_id}/match` |
| GET | `/budgets/{budget_id}/performance` |
| GET | `/budgets/{budget_id}/forecast` |

### Cash plans

| Method | Path |
|--------|------|
| POST | `/cash-plans` |
| GET | `/cash-plans` |
| GET | `/cash-plans/{cash_plan_id}` |
| PATCH | `/cash-plans/{cash_plan_id}` |
| POST | `/cash-plans/{cash_plan_id}/archive` |
| POST | `/cash-plans/{cash_plan_id}/items` |
| PATCH | `/cash-plans/{cash_plan_id}/items/{item_id}` |
| DELETE | `/cash-plans/{cash_plan_id}/items/{item_id}` (cancel) |
| POST | `/cash-plans/{cash_plan_id}/items/{item_id}/match` |
| POST | `/cash-plans/{cash_plan_id}/suggestions/generate` |
| POST | `/cash-plans/{cash_plan_id}/suggestions/accept` |
| GET | `/cash-plans/{cash_plan_id}/projection?scenario=expected&granularity=day` |
| GET | `/cash-plans/{cash_plan_id}/alerts` |
| GET | `/planning/summary` |

### Auth

- Reads: organization member
- Writes (create/update/match): owner / admin / member (`RequireWriter`)
- Close / archive: owner / admin (`RequireManager`)

### Scenarios (projection)

- `committed` — confirmed or 100% probability remaining amounts
- `expected` — probability-weighted inflows; full outflows
- `optimistic` — all remaining planned amounts

`safe_to_spend` = max(0, liquid − committed outflows − tax reserve shortfall − cash buffer). Operational estimate only.

## Notes

Persistence repositories under `infrastructure/repositories` may still be stubs until models land; application commands/queries are wired against domain Protocols.
