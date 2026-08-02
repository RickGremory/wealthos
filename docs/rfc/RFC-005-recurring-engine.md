# RFC-005 — Recurring Engine

| Field | Value |
|-------|-------|
| **Status** | Accepted (9.1–9.2) |
| **Created** | 2026-08-01 |
| **Epic** | [EPIC-008](../epics/EPIC-008-recurring-engine.md) |
| **Sprint** | [Sprint 9](../roadmap/sprint-9-recurring-engine.md) · [9.1](../roadmap/sprint-9.1-recurring-domain-model.md) · [9.2](../roadmap/sprint-9.2-recurrence-generation.md) |
| **Decision** | [2026-08-01-recurring-expectations-not-facts](../decisions/2026-08-01-recurring-expectations-not-facts.md) · [identity vs effective date](../decisions/2026-08-01-recurrence-identity-vs-effective-date.md) |

---

## Problem

WealthOS needs repeating financial expectations (salary, rent, subscriptions, savings transfers) without treating those expectations as ledger facts. Planning already consumes a Recurring adapter stub; Calendar must not invent a second expansion engine.

## Goals

1. Model **RecurringRule** as the persistent aggregate.  
2. Project **RecurringOccurrence** on demand for a bounded period.  
3. Stable `occurrence_key` shared with Planning (Sprint 8.3).  
4. Exceptions + pauses without rewriting history.  
5. Explicit confirmation before any Transaction is created.  

## Non-goals (V1)

Auto-create transactions · free RRULE UI · business-day calendars · FX transfers · statistical amount prediction · Timeline events per future occurrence · persisting infinite future rows.

---

## Core model

### RecurringRule (aggregate)

Persists configuration only. Product name: **Movimiento recurrente**.

Key attributes: org, name, direction (`inflow`/`outflow`/`transfer`), expected `amount` + `amount_strategy`, `currency`, `certainty`, `RecurrencePattern`, `invalid_date_policy`, `starts_on`/`ends_on`, accounts/category, `source_type` + optional related resource, `settlement_mode`, `status`, optional `grace_period_days`, version/timestamps.

### RecurrencePattern (frozen VO)

| Frequency | Required shape |
|-----------|----------------|
| `daily` | `interval` only |
| `weekly` | `interval` + normalized `days_of_week` (≥1) |
| `monthly` | `interval` + exactly one of `day_of_month` or `end_of_month` |
| `yearly` | `interval` + `month_of_year` + (`day_of_month` or `end_of_month`) |

`interval >= 1`. Anchor sequences to `starts_on` (never “from today”).

### RecurringOccurrence (projected VO)

Not a table of futures. Built by `RecurrenceGenerator` for `[period_start, period_end]`.

Carries `occurrence_key`, `original_expected_on`, `expected_on`, `expected_at`, money, certainty, derived status, optional link to transaction, exception flags.

Key format:

```text
recurring:{rule_id}:occurrence:{original_expected_on:%Y-%m-%d}
```

### RecurringRulePause

Historical pause intervals. Exclude dates inside windows. No retroactive fill on resume.

### RecurringOccurrenceException

Per original occurrence: `skip` or override date/amount/certainty. Identity remains the original key.

---

## Generation engine (9.2)

`RecurrenceGenerator.generate(...)` is pure and deterministic. Frequency strategies (`Daily` / `Weekly` / `Monthly` / `Yearly`) emit base dates only; the orchestrator applies pauses (on base date), exceptions, settlements, status via explicit `evaluated_on`, and stable sort `(expected_on, occurrence_key)`.

- Anchor all intervals on `starts_on`; inclusive `ends_on`.  
- Identity: `original_expected_on` → key. Display/filter: `expected_on`.  
- Limits: max 366-day request window; max 1000 occurrences — fail loud.  
- Exception loading must cover originals or replacements intersecting the period.  

Details and test matrix: [Sprint 9.2](../roadmap/sprint-9.2-recurrence-generation.md).

---

## Planning / Calendar ports

```text
RecurringPlanningService.preview_occurrences(org, currency, period_start, period_end)
  → RecurringOccurrence*
```

Planning maps each active occurrence → `PlanningCashFlow` preserving `occurrence_key`.  
Calendar consumes the same projection. Ownership: Commitment/Goal/Tax-sourced rules edit in owner modules.

---

## Transaction link

Preferred fields on Transaction (names may map to existing metadata):

- `source_occurrence_key`  
- optional `related_resource_type` / `related_resource_id`  

Settlement default: one linked transaction settles the occurrence even if amount differs (show delta).

---

## Module layout (target)

```text
modules/recurring/
  domain/ entities | enums | value_objects | services | policies | ports
  application/
  infrastructure/
  api/
```

Aligns with ADR-007 modular boundaries. Owning modules may expose adapters implementing Recurring/Planning ports.

---

## Success criteria

See Sprint 9.1 (model) and Sprint 9.2 (generator) acceptance checklists. Engine must be unit-testable without DB before API ships (9.3+).

## Open points → later slices

| Topic | Slice |
|-------|--------|
| Exact expansion algorithms | **9.2 Accepted** |
| Tables / Alembic / repositories / lifecycle commands | 9.3 |
| Confirm UI + series edit UX | 9.4 |
| Executable SPEC | 9.5 |
| Structural rule versioning table | after MVP if needed |
