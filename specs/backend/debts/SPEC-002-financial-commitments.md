# SPEC-002

# Financial Commitments — End-to-End Implementation

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Author** | Ricardo Balam |
| **Created** | 2026-07-25 |
| **Parent Epic** | [EPIC-005](../../../docs/epics/EPIC-005-debts.md) |
| **Parent RFC** | [RFC-002](../../../docs/rfc/RFC-002-financial-commitments.md) |
| **Design pillars** | [6.1](../../../docs/roadmap/sprint-6-financial-commitments.md)–[6.4](../../../docs/roadmap/sprint-6.4-payment-strategies.md) |
| **Detail brief** | [Sprint 6.5](../../../docs/roadmap/sprint-6.5-implementation-spec.md) |

> Once **Completed**, this SPEC is immutable. Further changes require a new SPEC.  
> Module package remains `modules/debts/`. Public API and UI use **commitments / Obligaciones**.

---

## 1. Objective

Ship Financial Commitments end-to-end so a user can:

1. Create a commitment linked to a liability account  
2. See derived balance, display status, and **next action**  
3. Rank obligations via org payment strategy (Avalanche / Snowball / Minimum only / Manual)  
4. Register a payment as an existing **transfer**  
5. See the commitment enrich Dashboard, Calendar, and Timeline-ready events  

Without storing a second balance on `debts`.

---

## 2. Scope

### Included

- List / summary (per currency) / create / edit / detail  
- Pause, resume, close (product), archive  
- Payment strategy projection + org `debt_strategy`  
- Derived next action + display status (backend-owned)  
- Activity from Transactions + domain events (no duplicate payment table)  
- Payment via transfer deep-link / prefilled flow  
- Dashboard `financial_commitments` projection  
- Calendar commitment events (projected)  
- Timeline-ready domain/observability events (no full Timeline UI required)  
- Responsive UI at `/app/commitments`  
- Unit, integration, and E2E tests  

### Design contracts already frozen

RFC-002 · Sprint 6.2 UX · 6.3 Integration · 6.4 Strategies · settled vs paid_off

---

## 3. Out of Scope

- Bank import, auto-pay, full amortization simulators  
- Refinance / consolidation / credit offers  
- AI recommendations, push/email notifications  
- FX conversion / summing currencies  
- Detailed multi-MSI under one card  
- Full Financial Timeline UI (events only)

---

## 4. Architecture Overview

```text
UI Obligaciones (/app/commitments)
        │
        ▼
Public API  /organizations/{id}/commitments
        │
        ▼
modules/debts/  (Debt aggregate)
        │
        ├──► Account (liability, 1:1 UNIQUE)
        ├──► Transactions (payments / charges / adjustments)
        ├──► Dashboard projection (financial_commitments)
        ├──► Calendar events (projected)
        └──► Org debt_strategy + DebtStrategyService
```

**Invariants:** balance never on Debt · payments = transfers · strategies orient only · multi-currency groups never summed · org isolation · optimistic `version` on writes.

**Persistent status:** `active` | `paused` | `defaulted` | `closed` | `archived`  
**Do not persist `paid_off`.** Display statuses (`settled`, `paid_off`, `overdue`, …) are **derived** and returned by the API.

**DebtBehavior:** `revolving` | `installment` — derived from `debt_type`, not a required DB column in V1.

Interest rate storage: `Numeric(9, 6)` as **percent** (`42.5` → `42.500000`), never `0.425`. Document in module README.

Money: `Numeric(19, 4)` / Decimal — never float.

---

## 5. Deliverables

| # | Deliverable |
|---|-------------|
| D1 | Migration + Debt entity aligned to SPEC schema |
| D2 | Domain services: state, strategy, next action |
| D3 | CRUD + pause/resume/close/archive use cases |
| D4 | Public REST under `/commitments` (+ legacy `/debts` alias optional) |
| D5 | Summary + strategy + activity projections |
| D6 | Dashboard `financial_commitments` enrichment |
| D7 | Calendar commitment event projection |
| D8 | Nuxt routes, repository, composables, components |
| D9 | Transfer payment handoff + cache invalidation |
| D10 | Permissions matrix enforced on API |
| D11 | Tests: domain, application, API, unit FE, E2E |
| D12 | Demo seed sample commitment(s) |
| D13 | Module docs + OpenAPI types regen |

---

## 6. Directory Structure

### Backend (responsibilities; files may be split as today)

```text
backend/src/wealthos/modules/debts/
  domain/          entities, VOs, events, exceptions, repos ports
  domain/services/ debt_state_service, debt_strategy_service, next_action_service
  application/     commands, queries, views/DTOs
  infrastructure/  models, mappers, sqlalchemy repos, projections
  api/             router, schemas, dependencies   # (= presentation)
```

Converge existing debts code to this contract (creditor, priority, optional rates, statuses, commitments routes, strategy hierarchy).

### Frontend

```text
frontend/
  pages/app/commitments/index.vue | new.vue | [id]/index.vue | [id]/edit.vue
  components/commitments/*        # see Sprint 6.5 brief
  composables/use-commitment*.ts
  repositories/commitments.repository.ts
  types/commitments.ts
  utils/commitment-*.ts
```

Follow existing Nuxt layout conventions (`pages/app/...`, kebab composables) even if the brief uses PascalCase filenames.

### Routes

| Path | Purpose |
|------|---------|
| `/app/commitments` | Overview |
| `/app/commitments/new` | Two-step create |
| `/app/commitments/:id` | Detail |
| `/app/commitments/:id/edit` | Edit |
| `/app/transactions/new?type=transfer&destination_account_id=…&source=commitment&commitment_id=…` | Payment |

Nav label: **Obligaciones** / Financial Commitments — top-level, not under Accounts.

---

## 7. Technologies

- Backend: FastAPI, SQLAlchemy 2, Alembic, Decimal, Pytest  
- Frontend: Nuxt 3, Vue 3, TypeScript, Pinia/composables, Zod (or project schema lib), Vitest, Playwright  
- Money as strings on the wire  

---

## 8. Implementation Plan

### Phase 1 — Persistence & domain

- [x] Migration `debts` columns per schema below  
- [x] `UNIQUE(account_id)` · indexes (org+status, org+currency, org+due_day, org+priority)  
- [x] Entity + enums + derived display status + due-day month-end rule (31→last day)  
- [x] Domain tests  

**Table `debts` (core columns):**  
`id`, `organization_id`, `account_id`, `name`, `debt_type`, `creditor`, `currency`, `status`, `priority`, `interest_rate`, `minimum_payment`, `scheduled_payment`, `credit_limit`, `original_amount`, `statement_day`, `due_day`, `maturity_date`, `notes`, `closed_at`, `archived_at`, `created_at`, `updated_at`, `version`

Required NOT NULL: org, account, name, debt_type, currency, status, priority.

### Phase 2 — CRUD lifecycle

- [x] Create / list / get / patch (optimistic `version` → 409 `concurrent_update`)  
- [x] Pause / resume / close / archive  
- [x] Validations: liability account, same org, currency match, not already linked, day ranges, non-negative amounts/rates  

### Phase 3 — Projections

- [x] `GET …/commitments/summary` (currency groups)  
- [x] Next action service  
- [x] `GET/PATCH …/commitments/strategy` (`DebtStrategyService`)  
- [x] `GET …/activity` (transactions + domain events)  
- [x] Utilization % when credit_limit present  

### Phase 4 — Frontend base

- [x] Repository + cache keys + composables  
- [x] Overview: header, summary, needs attention, strategy, filters, cards  
- [x] Create (type → form; inline liability account create)  
- [x] Detail (next action first)  

### Phase 5 — Payments

- [x] “Registrar pago” → transfer flow prefilled  
- [x] Central cache invalidation (accounts, commitments, dashboard, goals, calendar, timeline keys)  

### Phase 6 — Ecosystem

- [x] Dashboard widget projection  
- [x] Calendar events  
- [x] Audit + product analytics (no PII balances/names in analytics)  

### Phase 7 — Quality

- [x] Responsive + a11y  
- [x] Partial error states  
- [x] E2E flows (card, loan, multi-currency, viewer, statuses)  
- [x] Demo seed  

### Public API (canonical)

```text
GET/POST    /api/v1/organizations/{org_id}/commitments
GET         /api/v1/organizations/{org_id}/commitments/summary
GET/PATCH   /api/v1/organizations/{org_id}/commitments/strategy
GET/PATCH   /api/v1/organizations/{org_id}/commitments/{id}
POST        .../pause | resume | close | archive
GET         .../activity
```

Default list sort: attention desc → next due asc → balance desc → created_at desc.

Stable error codes: `commitment_not_found`, `account_not_liability`, `account_already_linked`, `account_currency_mismatch`, `concurrent_update`, `strategy_missing_required_data`, … (full list in Sprint 6.5 brief).

### Permissions (API enforces)

| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| View | ✓ | ✓ | ✓ | ✓ |
| Create / edit / pay / pause | ✓ | ✓ | ✓ | ✗ |
| Strategy / close / archive | ✓ | ✓ | ✗ | ✗ |

---

## 9. Acceptance Criteria

### Functional

- [x] Create commitment linked 1:1 to liability account; no stored balance on debt  
- [x] List shows backend-derived `displayStatus` + `nextAction`  
- [x] Payments only via existing transfer system  
- [x] Detail activity reuses Transactions (+ domain events)  
- [x] Avalanche / Snowball / Minimum only / Manual with reason codes; overdue hierarchy first  
- [x] Currencies never summed  
- [x] Dashboard + Calendar consume projections  
- [x] Backend permissions; UI does not rely on hiding alone  
- [x] Mobile + desktop; loading / empty / error / restricted / partial  
- [x] E2E main card → pay → balances/strategy update  

### Definition of done (golden path)

```text
Create card → link liability → balance reflected → due date + next action
→ strategy ranking → Dashboard + Calendar → register transfer payment
→ balances update → commitment/strategy/net worth refresh → timeline-ready event
```

### Non-functional

- [x] List &lt; 500 ms typical (ex-network); no N+1; pagination required  
- [x] Decimal money; tenant isolation; audit on writes; `correlation_id` on events  
- [x] Keyboard a11y; usable from 320px; `prefers-reduced-motion`  

---

## 10. Commit Plan

1. `feat(debts): add financial commitment persistence model`  
2. `feat(debts): implement commitment domain rules`  
3. `feat(debts): add commitment CRUD use cases`  
4. `feat(api): expose financial commitments endpoints`  
5. `feat(debts): add commitment summary projection`  
6. `feat(debts): implement payment strategy projection`  
7. `feat(debts): add next action recommendations`  
8. `feat(frontend): add commitments repository and composables`  
9. `feat(frontend): implement commitments overview`  
10. `feat(frontend): implement commitment creation flow`  
11. `feat(frontend): implement commitment detail page`  
12. `feat(transactions): support commitment payment flow`  
13. `feat(dashboard): add commitments projection`  
14. `feat(calendar): add commitment events`  
15. `feat(timeline): add commitment activity events`  
16. `test(commitments): add end-to-end commitment flows`  
17. `docs(commitments): document financial commitments module`  

---

## 11. Risks

| Risk | Mitigation |
|------|------------|
| Existing `debts` code diverges from RFC/SPEC | Converge in Phase 1–3; tests lock derived status + strategy honesty |
| Persist `paid_off` today | Migrate to `closed` + derived display; see settled decision |
| Public path `/debts` vs `/commitments` | Prefer `/commitments`; temporary alias if needed |
| Cache cross-module coupling | Central invalidation registry / app events |
| MSI fields ahead of persistence | Form must not promise unpersisted fields |
| Strategy exact-savings temptation | Educational copy only (6.4) |

---

## 12. Definition of Done

- [x] All Phase 1–7 checkboxes complete  
- [x] Commit plan landed (or equivalent focused commits covering the same surface)  
- [x] Golden path demoed on local stack with demo seed  
- [x] OpenAPI types regenerated for frontend  
- [x] SPEC status → **Completed**  
- [x] Epic/backlog/README updated  

---

## Related detail

Full UI copy, component inventory, Zod schemas, cache key helpers, test matrices, indexes, and analytics event names: [Sprint 6.5 Implementation Spec](../../../docs/roadmap/sprint-6.5-implementation-spec.md).
