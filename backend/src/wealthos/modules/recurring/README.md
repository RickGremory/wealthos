# Recurring Engine

Module: `wealthos.modules.recurring`

Implements [SPEC-005](../../../../../specs/backend/recurring/SPEC-005-recurring-engine.md).

## Progress

| Phase | Status |
|-------|--------|
| PR1 Persistence (5 tables, aggregate, repos) | Done |
| PR2 Recurrence generator + strategies | Done |
| PR3 Lifecycle commands | Done |
| PR4 Read/write HTTP APIs + queries | Done |
| PR5 Settlements ↔ Transactions | Done |
| PR6 Planning/Calendar/Dashboard adapters | Done |
| PR7–8 Frontend Recurrentes | Done |
| PR9 Hardening + E2E | Done |

## HTTP surface

Base: `/api/v1/organizations/{organization_id}/recurring`

| Method | Path | Notes |
|--------|------|-------|
| GET | `/` | List rules (+ next occurrence) |
| POST | `/` | Create rule |
| POST | `/preview` | Preview unsaved pattern |
| GET | `/occurrences` | Expand occurrences in period |
| GET | `/calendar-events` | Calendar slice (open occurrences) |
| GET | `/{rule_id}` | Detail + upcoming |
| GET | `/{rule_id}/versions` | Version history |
| POST | `/{rule_id}/preview` | Preview saved rule |
| POST | `/{rule_id}/versions` | New version |
| PATCH | `/{rule_id}` | Metadata |
| POST | `/{rule_id}/pause` | Pause |
| POST | `/{rule_id}/resume` | Resume |
| POST | `/{rule_id}/end` | End |
| POST | `/{rule_id}/archive` | Archive |
| POST | `/{rule_id}/exceptions` | Create exception |
| DELETE | `/{rule_id}/exceptions/{exception_id}` | Deactivate exception |
| POST | `/{rule_id}/settlements` | Link existing transaction |
| POST | `/{rule_id}/settlements/{id}/unlink` | Soft-void settlement |

Confirm flow: `POST /transactions` with `source.type=recurring_occurrence` + `occurrence_key` creates Transaction **and** settlement atomically. Voiding the transaction voids active settlements.

Adapters share `RecurringOccurrenceProjector` (manual rules only for Planning/Dashboard; Calendar includes transfers). Externally managed rules are excluded from Recurring Planning to avoid double-count.

Occurrences are expanded on read — never persisted as future rows.

## Hardening (PR9)

- Roles: viewer read; member write/confirm/skip/pause; owner/admin end+archive (`RequireWriter` / `RequireManager`)
- Timeline: `recurring.rule.*`, `recurring.exception.*`, `recurring.settlement.*`
- Audit logs: `audit.recurring.*` (org/actor/rule ids only — no amounts/names/notes)
- Metrics: `timed("recurring.preview|planning_adapter")` + structured counters
- E2E: `frontend/tests/e2e/recurring-lifecycle.spec.ts`
