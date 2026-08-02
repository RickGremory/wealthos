# Sprint 9.3 — Persistence, Commands & Lifecycle

**Status:** Accepted  
**Parent:** [Sprint 9](./sprint-9-recurring-engine.md)  
**Contract:** [RFC-005](../rfc/RFC-005-recurring-engine.md)  
**Decision:** [Rule + RuleVersion from day one](../decisions/2026-08-01-recurring-rule-versioning.md)  
**Depends on:** [9.1](./sprint-9.1-recurring-domain-model.md) · [9.2](./sprint-9.2-recurrence-generation.md)

---

## Objective

Turn the theoretical Recurring model into a **persistent module**: tables, repositories, commands, APIs, safe edit, effective versioning, pauses, exceptions, archive, and Planning integration.

Equivalent in spirit to Accounts / Goals going from domain → full module. **No production code in this slice** — schema + command contracts + ports; implementation lands in 9.5 / SPEC.

At the end of 9.3 the following are locked:

- four persistent tables (no `recurring_occurrences`);
- **Rule + RuleVersion** separation from day one;
- aggregate repository + commands / queries;
- HTTP API including reusable preview;
- Planning/Calendar consume projection port — not ORM tables.

---

## Module layout (target)

```text
modules/recurring/
├── domain/
├── application/
│   ├── commands/
│   ├── queries/
│   ├── dto/
│   └── services/
├── infrastructure/
│   ├── persistence/   # models, repositories, mappers
│   └── generator/     # DefaultRecurrenceGenerator (9.2)
├── api/               # router, schemas, dependencies
└── tests/
```

Aligns with ADR-007 modular boundaries.

---

## Persistence: four tables, zero future rows

| Table | Role |
|-------|------|
| `recurring_rules` | Series identity, provenance, lifecycle status |
| `recurring_rule_versions` | Temporal configuration (money, pattern, accounts) |
| `recurring_rule_pauses` | Pause windows (independent entities) |
| `recurring_occurrence_exceptions` | Per-occurrence overrides |

**No** `recurring_occurrences` table — occurrences remain calculated ([9.1](./sprint-9.1-recurring-domain-model.md)).

---

## `recurring_rules` (series shell)

Holds identity and lifecycle — **not** amount / frequency / currency / day_of_month (those live on versions).

| Column | Notes |
|--------|--------|
| `id`, `organization_id` | Tenant root |
| `source_type` | `manual` \| `commitment` \| `goal` \| `tax` \| `system` \| `imported` |
| `related_resource_type`, `related_resource_id` | Optional owner link |
| `status` | `active` \| `paused` \| `ended` \| `archived` |
| `created_at`, `updated_at`, `archived_at` | |
| `version` | Optimistic lock |

Externally managed rules (`source_type ≠ manual`) reject structural edits from Recurring UI/API (redirect to owner module).

---

## `recurring_rule_versions` (configuration with validity)

Primary configuration store. One rule may have many non-overlapping versions.

| Group | Fields |
|-------|--------|
| Identity | `id`, `recurring_rule_id` |
| Validity | `effective_from`, `effective_until` (nullable = open) |
| Money | `name`, `direction`, `currency`, `amount`, `amount_strategy`, `certainty` |
| Pattern | `frequency`, `interval`, days/month flags, `invalid_date_policy`, `grace_period_days` |
| Series bounds | `starts_on`, `ends_on` (series generation bounds on this version slice) |
| Accounts | `account_id`, `destination_account_id`, `category_id` |
| Meta | `notes`, `settlement_mode`, `created_at`, `version` (optimistic lock) |

### Why Rule ≠ Version

Example: Netflix 800 MXN → 950 MXN from September.

- Same `RecurringRule.id`  
- V1: 800, `effective_until = 31 Aug`  
- V2: 950, `effective_from = 1 Sep`  

History, Planning keys, and linked transactions stay coherent.

**Invariant:** effective periods for the same rule **must not overlap**.

At create time there is always at least one version (often the only one for months) — versioning is not deferred.

---

## Pauses & exceptions

### `recurring_rule_pauses`

`id`, `recurring_rule_id`, `starts_on`, `ends_on` (nullable = open), `reason`, `created_at`, `version`.

Not versioned with rule config. At most **one open pause** per rule.

### `recurring_occurrence_exceptions`

`id`, `recurring_rule_id`, `organization_id`, `original_occurrence_key`, `original_expected_on`, `exception_type`, optional replacements (`expected_on` / `amount` / `certainty`), `reason`, timestamps, soft-delete (`deleted_at` or `is_active`), `version`.

Unique active exception per `(rule_id, original_occurrence_key)`. Soft-delete preferred over hard delete (history).

---

## Indexes (minimum)

| Table | Indexes |
|-------|---------|
| rules | `(organization_id, status)` |
| versions | `(recurring_rule_id, effective_from)`, `(recurring_rule_id, effective_until)` |
| pauses | `(recurring_rule_id, starts_on)` |
| exceptions | `(recurring_rule_id, original_occurrence_key)`, plus query support for `replacement_expected_on` / `original_expected_on` affecting a period |

Alembic migration creates all four tables + indexes in one revision (number assigned at implement time).

---

## Repositories

| Port | Responsibility |
|------|----------------|
| `RecurringRuleRepository` | Series shell CRUD / lock |
| `RecurringRuleVersionRepository` | Versions; non-overlap checks; versions affecting period |
| `RecurringPauseRepository` | Pauses; open-pause uniqueness |
| `RecurringExceptionRepository` | Exceptions; `list_affecting_period(rule, start, end)` |
| **`RecurringAggregateRepository`** | Load/save `RecurringAggregate` for commands |
| `RecurringProjectionRepository` | Read path for Planning/Calendar preview across org |

Application commands prefer the **aggregate** repository, not four ad-hoc fetches.

### Aggregate

```text
RecurringAggregate
  ├── Rule
  ├── Versions (ordered, non-overlapping)
  ├── Pauses
  └── Exceptions (active)
```

---

## Commands

| Command | Behavior |
|---------|----------|
| `CreateRecurringRule` | Insert rule + initial version; commit |
| `UpdateRecurringRule` | See edit policy below |
| `ArchiveRecurringRule` | `status=archived`, `archived_at`; never hard-delete with history |
| `PauseRecurringRule` | Create pause interval (reject if open pause exists) |
| `ResumeRecurringRule` | Close open pause (`ends_on = today` or supplied date) |
| `CreateOccurrenceException` | skip / reschedule / amount / override |
| `RemoveOccurrenceException` | Soft-deactivate; do not erase history |

Optimistic locking on rule/version/exception via `version` column.

### Edit policy (`UpdateRecurringRule`)

| Kind | Examples | Persistence |
|------|----------|-------------|
| **Simple** | name, notes, category (descriptive) | Update **current** version in place |
| **Structural** | amount, frequency, day, currency, accounts, direction, certainty, pattern, grace | Require `effective_from`; close current version (`effective_until = day before`); insert new version |

Structural edits on externally managed rules → reject.

Domain event (for future Timeline, not Timeline spam of occurrences): `RecurringRuleUpdated` on structural change; also created / archived events as needed.

---

## Queries

| Query | Use |
|-------|-----|
| `GetRecurringRule` | Detail + current version |
| `ListRecurringRules` | Org list (filter status, source) |
| `PreviewOccurrences` | Bounded generation via 9.2 engine |
| `ListExceptions` / `ListPauses` | Diagnostics / UI |

### Preview orchestration

1. Resolve versions affecting `[start, end]` (non-overlapping slices).  
2. For each version, call `RecurrenceGenerator` with that version’s config and clipped range.  
3. Load pauses + exceptions affecting period + settlements.  
4. Merge, sort, enforce limits.  
5. Return DTO list — **consumers never see version IDs as identity of money movement** (key stays `recurring:{rule_id}:occurrence:{date}`).

`RecurringPreviewItem`: `occurrence_key`, `expected_on`, `expected_amount`, `status`, `is_exception`, optional `source_version_id` (debug/UI only).

---

## HTTP API (sketch)

Base under org-scoped API (same style as planning/commitments).

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/recurring` | List |
| `POST` | `/recurring` | Create |
| `GET` | `/recurring/{id}` | Get |
| `PATCH` | `/recurring/{id}` | Update (simple vs structural + `effective_from`) |
| `DELETE` | `/recurring/{id}` | **Archive** (user delete → archive) |
| `POST` | `/recurring/{id}/pause` | Pause |
| `POST` | `/recurring/{id}/resume` | Resume open pause |
| `POST` | `/recurring/{id}/exceptions` | Create exception |
| `PATCH` | `/recurring/{id}/exceptions/{exception_id}` | Update active exception |
| `DELETE` | `/recurring/{id}/exceptions/{exception_id}` | Soft-remove |
| `GET` | `/recurring/{id}/preview?start=&end=` | Single-rule preview |
| `GET` | `/recurring/preview?start=&end=&currency=` | Org-wide preview (Planning/Calendar) |

AuthZ: organization membership; multi-tenant isolation on every query.

Money amounts as **strings** in JSON (project convention).

---

## Planning & Calendar integration

```text
Planning / Calendar
  → RecurringProjectionRepository.preview_occurrences(org, currency, period)
  → RecurringOccurrence*
  → PlanningCashFlow / calendar item
```

- Planning does **not** join Recurring tables or re-expand RRULE math.  
- Skipped / cancelled filtered for STS; Calendar may show skipped muted.  
- Replaces Sprint 8 Recurring adapter stub.

Timeline: **not** in 9.3 beyond publishing domain events for create/update/archive. No event per future occurrence.

---

## Lifecycle (product)

```text
Create → Version A → (structural) Version B → … → Archive
                ↘ Pause window(s) ↗
                ↘ Exceptions on keys ↗
```

Never destroy history for rules that produced exceptions or settlements. Physical delete only if never related and clearly a mistake — product default: **archive**.

---

## Tests (required in SPEC / 9.5)

| Layer | Cases |
|-------|--------|
| Commands | create + initial version; simple vs structural update; archive; pause/resume; exception create/soft-remove; open-pause uniqueness; version non-overlap |
| Repositories | org isolation; optimistic lock conflict; `list_affecting_period`; versions affecting period |
| Generator wiring | multi-version period merge; no duplicate base dates across adjacent versions |
| API | CRUD/archive; preview; authorization; externally managed reject |

---

## Acceptance criteria (9.3)

- [x] Four tables defined; **no** persisted future occurrences  
- [x] Rule shell vs Version configuration separated from day one  
- [x] Structural edits require `effective_from` and non-overlapping versions  
- [x] Pauses independent; exceptions soft-deleted; keys unchanged  
- [x] Aggregate repository + command/query set locked  
- [x] Preview API reusable by UI, Planning, Calendar  
- [x] Planning consumes projection port only  
- [x] Optimistic lock + structural domain events specified  
- [x] Test matrix for commands / repos / API defined  

*(Design acceptance; code in 9.5 / SPEC.)*

---

## Main decision of 9.3

Adopt **Rule + RuleVersion** immediately (even when only one version exists). Rent/salary/subscription changes become new versions without rewriting history or breaking Planning keys.

## Next

**Sprint 9.4 — UX** — **Accepted** ([sprint-9.4-recurring-ux.md](./sprint-9.4-recurring-ux.md)). Next: **9.5** SPEC + hardening.
