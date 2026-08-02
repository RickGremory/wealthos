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
| PR5 Settlements ↔ Transactions | Pending |
| PR6 Planning/Calendar/Dashboard adapters | Pending |
| PR7–8 Frontend Recurrentes | Pending |
| PR9 Hardening + E2E | Pending |

## HTTP surface

Base: `/api/v1/organizations/{organization_id}/recurring`

| Method | Path | Notes |
|--------|------|-------|
| GET | `/` | List rules (+ next occurrence) |
| POST | `/` | Create rule |
| POST | `/preview` | Preview unsaved pattern |
| GET | `/occurrences` | Expand occurrences in period |
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

Occurrences are expanded on read — never persisted as future rows.
