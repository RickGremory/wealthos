# SPEC-005

# Recurring Engine — End-to-End Implementation

| Field | Value |
|-------|-------|
| **Status** | Ready |
| **Author** | Ricardo Balam |
| **Created** | 2026-08-01 |
| **Parent Epic** | [EPIC-008](../../../docs/epics/EPIC-008-recurring-engine.md) |
| **Parent RFC** | [RFC-005](../../../docs/rfc/RFC-005-recurring-engine.md) |
| **Design pillars** | [9.1](../../../docs/roadmap/sprint-9.1-recurring-domain-model.md)–[9.4](../../../docs/roadmap/sprint-9.4-recurring-ux.md) |
| **Detail brief** | [Sprint 9.5](../../../docs/roadmap/sprint-9.5-implementation-spec.md) |

> Once **Completed**, this SPEC is immutable. Further changes require a new SPEC.  
> Day-to-day coding follows this document. Do not reopen 9.1–9.4 for implementation debates.

---

## 1. Objective

Ship Recurring so a user can:

1. Create versioned recurring rules (inflow / outflow / transfer)  
2. Preview and list projected occurrences for a bounded period  
3. Pause, resume, end, archive; skip / reschedule / amount-override one occurrence  
4. Apply structural changes from an `effective_from` date (new version)  
5. Confirm an occurrence by creating a real **Transaction** (linked settlement)  
6. See the same forecasts in Planning, Calendar, and Dashboard upcoming  

without auto-posting ledger rows and without persisting infinite future occurrences.

---

## 2. Scope

### Included

- Five tables + Alembic (rules, versions, pauses, exceptions, **settlements**)  
- Pure `RecurrenceGenerator` (daily/weekly/monthly/yearly) + status resolver  
- Aggregate + lifecycle commands + queries  
- Org-scoped APIs (CRUD lifecycle, preview, occurrences, settlements)  
- Transactions integration (source context → atomic settlement link; void unlinks)  
- Planning adapter (replace stub); Calendar adapter; Dashboard slim projection  
- Dedup: externally managed rules excluded from generic Recurring Planning contribution  
- UI `/app/recurring` (+ new/detail); confirm/skip/reschedule/version/pause  
- Unit / integration / property / E2E critical paths  
- Permissions, audit events, observability  

### Out of scope

- Auto-create transactions · bank sync · heuristic auto-match · FX · business calendars · free RRULE · push/email · statistical amounts · mass-persist occurrences · Timeline spam per future occurrence  

---

## 3. Architecture

```text
UI Recurrentes (/app/recurring) + Calendar / Planning / Dashboard
        │
        ▼
API …/organizations/{id}/recurring/*
        │
        ├──► commands (create, version, pause, exception, settle, …)
        │         ↓
        │    RecurringAggregateRepository
        │
        └──► queries (list, detail, preview, occurrences)
                  ↓
            RecurrenceGenerator (pure) ← pauses, exceptions, settlements injected
                  ↓
            RecurringOccurrence*
                  ↓
            Planning / Calendar adapters (same keys)
```

**Invariants:** Decimal money · org isolation · no foreign ORM in domain/generator · no `date.today()` inside generator · `original_expected_on` owns key · confirm = Transaction · externally managed rules reject Recurring structural writes · never mix currencies.

---

## 4. Persistence

### `recurring_rules`

Series shell: `id`, `organization_id`, `source_type`, `related_resource_*`, `status`, timestamps, `archived_at`, `lock_version`.

### `recurring_rule_versions`

Config with `effective_from` / `effective_until` (non-overlapping). Money, pattern fields (`frequency`, `interval`, `days_of_week`, `day_of_month`, `month_of_year`, `end_of_month`, `invalid_date_policy`), `starts_on`/`ends_on`, accounts, category, certainty, settlement_mode, grace, notes, `created_by`, timestamps.

**Overlap:** prefer PostgreSQL `EXCLUDE` on `daterange` + `btree_gist` when available; always enforce in application transaction (lock versions → check → close → insert).

### `recurring_rule_pauses`

`starts_on`, `ends_on` (nullable = open), reason, actor, `lock_version`. Max one open pause per rule.

### `recurring_occurrence_exceptions`

`original_occurrence_key`, `original_expected_on`, type, optional replacements, `is_active`, soft deactivate fields. Unique active `(rule_id, original_occurrence_key)`.

### `recurring_occurrence_settlements`

Specialized link table (Recurring source of truth for settlement):

| Column | Notes |
|--------|--------|
| `occurrence_key`, `transaction_id` | UNIQUE pair |
| `settled_amount`, `link_type` | `explicit` \| `manual` \| `suggested_confirmed` |
| `voided_at` | set on transaction void |
| org, rule_id, actors, timestamps | |

Transactions may also store a generic `source` / `source_occurrence_key` for navigation — settlement table remains authoritative for Recurring status.

### Do not create

`recurring_occurrences` · `next_occurrence` as truth · `last_generated_at` as truth.

### Checks / indexes

- `amount > 0`, `interval >= 1`, valid date ranges  
- Indexes: org+status; version effective; pauses; exceptions original/replacement dates; settlements by occurrence_key  

---

## 5. Domain (V1)

### Aggregate

`RecurringAggregate(rule, versions, pauses, exceptions)` — immutable collections; behaviors: `current_version`, `versions_affecting`, `pause`/`resume`, `create_version`, `end`, `archive`, `create_exception`.

### Generator

As [9.2](../../../docs/roadmap/sprint-9.2-recurrence-generation.md): strategies per frequency; pauses on base date; exceptions by key; moved-into-range; `evaluated_on` explicit; limits 366 days / 1000 occurrences (fail loud).

### Commands (definitive)

`CreateRecurringRule` · `UpdateRecurringRuleMetadata` · `CreateRecurringRuleVersion` · `PauseRecurringRule` · `ResumeRecurringRule` · `EndRecurringRule` · `ArchiveRecurringRule` · `CreateRecurringOccurrenceException` · `DeactivateRecurringOccurrenceException` · `LinkRecurringOccurrenceTransaction` · `UnlinkRecurringOccurrenceTransaction`

**No** `CreateRecurringOccurrence` · **No** `GenerateRecurringTransactions`.

### Edit rules

- Metadata V1: prefer versioned fields; thin metadata patch only for non-structural display/admin notes if kept — structural (amount, pattern, accounts, category, certainty, currency, direction) → `CreateRecurringRuleVersion` with concrete `effective_from` (not `"next"`).  
- V1: `effective_from >= org-local today` (no normal UI retroactive structural change).  
- Resume: open pause `ends_on = resume_on - 1 day` so `resume_on` is eligible again.  
- Settled occurrence: block skip/reschedule; unlink is separate.  
- Confirm path: Transaction create with `source.type = recurring_occurrence` + key → **atomic** settlement link in monolith; void sets `voided_at` and restores expectation.

### Ports

Account/category validation ports (no Accounts ORM in domain). `RecurringAggregateRepository` + settlement/exception/occurrence-read specialists. Generator receives no repositories.

---

## 6. API (org-scoped)

Base: `/api/v1/organizations/{organization_id}/recurring`

```text
GET/POST     /recurring
GET          /recurring/{rule_id}
PATCH        /recurring/{rule_id}/metadata
POST         /recurring/{rule_id}/versions
POST         /recurring/{rule_id}/end
POST         /recurring/{rule_id}/archive
POST         /recurring/{rule_id}/pauses
POST         /recurring/{rule_id}/resume
POST         /recurring/{rule_id}/exceptions
POST         /recurring/{rule_id}/exceptions/{exception_id}/deactivate
GET          /recurring/occurrences          # period required
GET          /recurring/{rule_id}/occurrences
GET          /recurring/{rule_id}/occurrence?key=...
POST         /recurring/preview              # unsaved
POST         /recurring/{rule_id}/preview
POST         /recurring/{rule_id}/settlements
POST         /recurring/{rule_id}/settlements/{id}/unlink
```

Pattern schemas: discriminated union by `frequency`. Money as strings. Writes carry `expected_lock_version` → `409 concurrent_update`. Idempotency-Key on create rule/version/exception/settlement.

Stable error codes: see [9.4](../../../docs/roadmap/sprint-9.4-recurring-ux.md) + `retroactive_structural_change_not_allowed`, `pause_period_overlap`, transaction mismatch codes, etc.

Permissions: Viewer read-only; Member create/edit/confirm/skip/pause; End/Archive Owner+Admin; externally managed → `recurring_rule_managed_externally`.

---

## 7. Integrations

| Consumer | Behavior |
|----------|----------|
| **Planning** | Adapter lists occurrences; include upcoming/due/overdue/(partial remaining for cumulative); exclude settled/skipped/cancelled; **skip `source_type` managed externally** (owner module emits cash flow using Recurring generator if needed) |
| **Calendar** | Same occurrences; actions call Recurring commands |
| **Dashboard** | Slim upcoming (3–4) + pending confirmation count; currency-sliced |
| **Timeline** | Material rule events + skip/reschedule; confirmation narrative = Transaction event (avoid duplicate “confirmed” spam) |
| **Transactions** | Prefill source; atomic link; void → void settlement |

---

## 8. Frontend

Routes: `/app/recurring`, `/app/recurring/new`, `/app/recurring/[id]` · nav **Recurrentes**.  
Repository + composables + cache keys per [9.4](../../../docs/roadmap/sprint-9.4-recurring-ux.md). Preview debounced; never FE date expansion. Confirm via Transactions drawer/route with occurrence context.

---

## 9. Phases / DoD checklist

| Phase | Deliverable | Done when |
|-------|-------------|-----------|
| 1 | Persistence | 5 tables, migration, models, aggregate repo |
| 2 | Engine | Strategies + pauses/exceptions/status + property tests |
| 3 | Commands | Lifecycle + lock + events |
| 4 | Read API | List/detail/preview/occurrences |
| 5 | Settlements | Link/unlink + void handler + atomic confirm |
| 6 | Adapters | Planning (replace stub) + Calendar + Dashboard |
| 7 | FE overview | Nav, list, summary, attention, filters |
| 8 | FE lifecycle | Create, preview, detail, confirm, skip, version, pause |
| 9 | Hardening | Perms, audit, metrics, a11y, E2E, SPEC → Completed |

### Performance targets

Preview rule &lt; 100 ms · monthly list ≤100 rules &lt; 500 ms · pure engine 1000 occ &lt; 50 ms · batch-load versions/pauses/exceptions/settlements (no N+1).

### Sprint DoD

- [ ] Rule + versions non-overlapping; no mass-persisted occurrences  
- [ ] Correct frequencies; stable keys; pauses/exceptions; future versions  
- [ ] Confirm → Transaction + settlement; void restores expectation  
- [ ] Planning/Calendar share generator; no external-rule double count  
- [ ] No auto transactions; no FX mixing  
- [ ] Desktop + mobile; critical E2E green; audit + observability on  

---

## 10. Module layout

```text
modules/recurring/
  domain/   entities | value_objects | enums | services | policies | ports | events | exceptions
  application/ commands | queries | dto
  infrastructure/ persistence | planning | calendar
  api/
```

Frontend under `pages/app/recurring/`, `components/recurring/`, `repositories/recurring.repository.ts`, `types/recurring.ts`.

---

## 11. Observability & audit

**Metrics:** rule_created, preview_duration_ms, occurrences_generated, generation_failures, confirmed/skipped/rescheduled, settlement_linked, planning_adapter_duration_ms.

**Logs:** structured counts/durations/org ids — **no** amounts, names, notes, accounts.

**Audit:** `recurring.rule.*`, `recurring.exception.*`, `recurring.settlement.*` with actor, org, rule id, field diffs, correlation id.

---

## 12. Commit / PR convention

```text
feat(recurring): add versioned recurring rule persistence
feat(recurring): implement recurrence generation engine
feat(recurring): support pauses and occurrence exceptions
feat(recurring): add recurring lifecycle commands
feat(recurring): expose rule and occurrence queries
feat(recurring): add unsaved rule preview
feat(recurring): link occurrences with transactions
feat(transactions): support recurring occurrence context
feat(planning): integrate recurring cash flow occurrences
feat(calendar): show recurring financial events
feat(dashboard): include upcoming recurring movements
feat(frontend): add recurring overview | creation | detail | confirmation | skip/reschedule | versions
test(recurring): cover generation and lifecycle | settlement integration
test(e2e): cover recurring movement lifecycle
docs(recurring): …
```

PR order = phases 1→9 in section 9.
