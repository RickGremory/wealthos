# Sprint 6.5 — Financial Commitments Frontend & Implementation Specification

**Status:** Accepted (executable)  
**SPEC:** [SPEC-002](../../specs/backend/debts/SPEC-002-financial-commitments.md) ← **day-to-day contract**  
**Parent:** [Sprint 6](./sprint-6-financial-commitments.md)  
**Depends on:** RFC-002 · [6.2](./sprint-6.2-commitments-ux.md) · [6.3](./sprint-6.3-commitments-integration.md) · [6.4](./sprint-6.4-payment-strategies.md)

> This brief holds the detailed UI/API/test inventory.  
> Tick progress and commits on **SPEC-002**. Sprint 6 design is complete; implementation follows SPEC phases.

---

## Objective

Implement Obligaciones end-to-end, connected to Accounts, Transactions, Dashboard, Calendar, Organizations, Payment Strategies, and Financial Timeline events.

Philosophy unchanged: debts stress users — the UI must not. Strategies orient; transfers move money.

---

## 1. Scope

### Included

List, per-currency summary, create/edit, detail, archive/pause/close, strategy, next action, transaction-based activity, transfer payments, derived states, Dashboard, Calendar/Timeline events, responsive UI, unit/integration/E2E tests.

### Out of scope

Bank import, auto-pay, full amortization, refinance, AI advice, push/email, FX conversion, credit offers, multi-MSI under one card.

---

## 2. Backend module

Internal package: `modules/debts/`. Public product language: **commitments**.

Preserve responsibilities even if files stay compact:

- Domain: entity, enums, events, exceptions, repos, `debt_state_service`, `debt_strategy_service`, `next_action_service`  
- Application: commands (create/update/pause/resume/archive/close/change_strategy), queries (get/list/summary/activity/strategy)  
- Infrastructure: models, mappers, projections  
- API: router, schemas, dependencies  

---

## 3. Persistent model

### Table `debts`

`id`, `organization_id`, `account_id`, `name`, `debt_type`, `creditor`, `currency`, `status`, `priority`, `interest_rate`, `minimum_payment`, `scheduled_payment`, `credit_limit`, `original_amount`, `statement_day`, `due_day`, `maturity_date`, `notes`, `closed_at`, `archived_at`, `created_at`, `updated_at`, `version`

**Constraints:** `UNIQUE(account_id)` · NOT NULL on org, account, name, debt_type, currency, status, priority.

**Money:** `Numeric(19, 4)` — never float.  
**Interest:** `Numeric(9, 6)` stored as **percent** (`42.5` → `42.500000`), never `0.425`.

### Indexes

```text
(organization_id, status)
(organization_id, currency)
UNIQUE (account_id)
(organization_id, due_day)
(organization_id, priority)
```

Search V1: normal indexes / `ILIKE` — no search engine.

---

## 4. Persistent vs display status

### Persistent

```ts
type DebtStatus = "active" | "paused" | "defaulted" | "closed" | "archived";
```

Do **not** persist `paid_off`.

### Derived display (API returns; FE must not reimplement)

```ts
type CommitmentDisplayStatus =
  | "active" | "due_soon" | "overdue" | "settled"
  | "paid_off" | "paused" | "defaulted" | "archived";
```

Rules (order matters): archived → defaulted → paused → overdue → due_soon → settled (revolving, balance 0, open) → paid_off (closed + balance 0) → active.

### Behavior (derived from type)

`revolving`: credit_card, line_of_credit  
`installment`: mortgage, auto/personal/business/student/family loan, installment_plan, …

---

## 5. Public API

Base: `/api/v1/organizations/{organization_id}/commitments`

| Method | Path | Notes |
|--------|------|-------|
| GET/POST | `/commitments` | List filters: status, type, priority, currency, search, sort, page, page_size |
| GET | `/commitments/summary` | Per-currency groups |
| GET/PATCH | `/commitments/strategy` | Org strategy projection |
| GET/PATCH | `/commitments/{id}` | PATCH includes `version` |
| POST | `.../pause` `.../resume` `.../close` `.../archive` | close = product closed, not manual wipe |
| GET | `.../activity` | Transactions + domain events |

Default sort: attention desc → next_due asc → balance desc → created_at desc.

### Create validation

Same org · liability account · currency match · account not linked · day 1–31 · non-negative amounts/rates · edit permission.

### Concurrency

Optimistic `version` → `409` + `concurrent_update`.

### Error envelope

```json
{
  "error": {
    "code": "account_already_linked",
    "message": "The account is already linked to another commitment.",
    "details": { "account_id": "uuid" }
  }
}
```

FE translates by `code`. Stable codes listed in SPEC-002 / §10 of the product draft: `commitment_not_found`, `account_not_liability`, `account_already_linked`, `account_currency_mismatch`, `commitment_already_archived`, `commitment_already_paused`, `commitment_not_paused`, `commitment_has_outstanding_balance`, `invalid_due_day`, `invalid_statement_day`, `invalid_interest_rate`, `invalid_payment_amount`, `organization_access_denied`, `strategy_not_supported`, `strategy_missing_required_data`, `concurrent_update`.

### Due day 29–31

If day missing in month → **last day of month**. Backend owns the rule + tests; FE shows computed date.

---

## 6. DTOs (money as strings)

### List item

`id`, `name`, `type`, `creditor`, `account{id,name}`, `currency`, `currentBalance`, `displayStatus`, `priority`, `requiredPayment`, `requiredPaymentType` (`minimum`|`scheduled`|null), `nextDueDate`, `daysUntilDue`, `interestRate`, `creditLimit`, `utilizationPercentage`, `nextAction`.

### Summary

```ts
interface CommitmentSummary {
  groups: CommitmentCurrencySummary[];
  activeCommitments: number;
  commitmentsNeedingAttention: number;
  nextDue: CommitmentUpcomingDue | null;
}
```

Never combine MXN+USD into one total.

### Utilization

`balance / credit_limit × 100` when limit &gt; 0; hide if null; 0% if balance ≤ 0; allow &gt; 100%. Not a credit-score diagnosis — balance vs limit only. API computes.

---

## 7. Frontend structure

### Pages

`/app/commitments` · `/new` · `/:id` · `/:id/edit`

### Components (inventory)

SummaryGrid/Card · CommitmentCard (+ skeleton) · Filters · EmptyState · StatusBadge · TypeIcon · Form · TypeSelector · LiabilityAccountSelector · NextAction · DetailHeader · MetricsGrid · ActivityList · StrategyCard/Ranking/Selector · Archive/Pause/Close dialogs.

### Composables

`useCommitments` (filters, search debounce ~300ms, pagination, URL sync)  
`useCommitment` · `useCommitmentSummary` · `useCommitmentActivity` · `useCommitmentStrategy` · `useCommitmentMutations` (per-action pending, not one global `isLoading`).

### Repository

Components must not call `$fetch` directly — use `CommitmentsRepository` (list/summary/get/create/update/pause/resume/close/archive/activity/getStrategy/updateStrategy).

### Cache keys

Central `commitmentKeys`: `all`, `lists`, `list(filters)`, `detail`, `summary`, `strategy`, `activity`.

### Invalidation

| Event | Invalidate |
|-------|------------|
| Create | lists, summary, strategy, dashboard, calendar, timeline |
| Edit | detail, lists, summary, strategy, dashboard, calendar |
| Payment (from Transactions) | source+dest accounts, balances, commitment detail/summary/strategy/activity, dashboard, goals, planning, calendar, timeline |

Prefer app events / central invalidation registry over hard cross-imports.

### Payment deep link

```text
/app/transactions/new?type=transfer
  &destination_account_id={accountId}
  &source=commitment
  &commitment_id={commitmentId}
```

Suggest amount = required payment; description `Pago de {name}`; user picks source account. **No** `pay-commitment` endpoint.

---

## 8. Screen layouts

### Overview order

Header → Summary → Needs Attention → Payment Strategy → Search/Filters → Cards → Pagination.

Needs Attention order: overdue → due soon → defaulted → missing data. Urgent problems only — no optimization tips mixed in.

### Cards

Clickable as **link** (whole card). Inner buttons `stopPropagation`. Show: icon/name, type·creditor, status, balance, required payment, due, next action. Not every model field.

### Create — two steps

1. Type picker (card, mortgage, auto, personal, business, student, LOC, family, installment, other)  
2. Type-specific form (common + revolving vs installment vs MSI fields). Do not promise unpersisted MSI fields.

Inline **Create liability account** drawer/modal keeps form values and auto-selects new account.

### Detail order

Breadcrumbs → Header → **Next Action** → Metrics → Strategy context → Activity → Metadata → Danger zone.

Activity mixes transaction items and domain event items (overdue materialization must not spam on every read).

### Strategy panel

Show strategy, current priority debt + why, expandable ranking, partial-data warnings. Change strategy in-place (no extra route). Manual required for personal ordering.

---

## 9. Permissions

| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| View | ✓ | ✓ | ✓ | ✓ |
| Create / edit / pay / pause | ✓ | ✓ | ✓ | ✗ |
| Strategy / close / archive | ✓ | ✓ | ✗ | ✗ |

Backend is source of truth.

---

## 10. UI states

Per section: `idle` | `pending` | `success` | `empty` | `error` | `restricted` | `stale`.

**Partial errors:** strategy fail must not blank the whole page.

Empty copies: no commitments · no filter hits · no activity · strategy needs ≥2 actives.

---

## 11. a11y & responsive

- Text + color for status; visible labels; `aria-describedby` errors  
- Dialogs focus trap; keyboard card links; touch targets; `prefers-reduced-motion`; `aria-live` for confirmations  

| Breakpoint | Summary | Cards |
|------------|---------|-------|
| Desktop | 4 cols | 2 cols when space |
| Tablet | 2 cols | 1–2 |
| Mobile | stack | 1 col; filters drawer; pay CTA easy to reach |

---

## 12. Dashboard / Calendar

Dashboard projection: per-currency totals + `activeCount` / `overdueCount` / `nextDue`. Multi-currency: separate groups or reduce to counts + next due — never one combined balance.

Calendar events (projected): `statement_date` | `payment_due` | `maturity_date` | `review_date` with severity `normal` | `attention` | `overdue`.

---

## 13. Observability vs audit

**Product analytics** (no balances, creditor, name, notes, payment amounts):  
`commitment_*_viewed|created|failed|updated|paused|resumed|closed|archived|payment_*|strategy_*|filter_applied`  
Safe props: `commitment_type`, `strategy`, `currency_count`, `source_screen`, `success`, `error_code`.

**Org audit:** create/update/pause/resume/close/archive/strategy_changed with actor, org, resource, timestamp, field diffs — avoid logging full sensitive notes.

---

## 14. Test matrix (summary)

**Domain:** liability-only, org match, unique account, currency, rates, derived status (settled vs paid_off), strategy hierarchy, no FX mix, day-31 rule.  
**Application/API:** CRUD lifecycle, strategy partial/full, 404/409/422, tenant isolation, version conflict.  
**FE unit:** formatters, labels, error map, Zod, query sync.  
**Components:** card, badge, next action, form, strategy, empty, partial error, multi-currency.  
**E2E:** card+inline account+pay · loan+calendar+avalanche · MXN+USD groups · viewer permissions · status gallery.

---

## 15. Implementation phases & commits

See **SPEC-002 §8 and §10** (canonical). Phases 1→7: persistence → CRUD → projections → FE base → payments → ecosystem → quality.

---

## 16. Definition of done

Sprint 6 is done when the golden path in SPEC-002 §9 works on a real local stack — not when a debts screen merely exists.

Design of Sprint 6 (6.1–6.5) is **complete**. Implementation tickets = SPEC-002 phases/commits.
