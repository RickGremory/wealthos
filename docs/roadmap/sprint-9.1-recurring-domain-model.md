# Sprint 9.1 — Recurring Domain Model

**Status:** Accepted  
**Parent:** [Sprint 9](./sprint-9-recurring-engine.md)  
**Contract:** [RFC-005](../rfc/RFC-005-recurring-engine.md)  
**Decision:** [Recurring expectations ≠ facts](../decisions/2026-08-01-recurring-expectations-not-facts.md)

---

## Objective

Design a Recurring Engine that can represent repeating inflows, outflows, and transfers; generate **stable future occurrences**; and feed Planning — **without** creating transactions automatically.

At the end of 9.1 the following are locked:

- recurring template (`RecurringRule`);
- temporal pattern (`RecurrencePattern`);
- projected occurrence (`RecurringOccurrence`);
- exceptions & pauses;
- lifecycle & statuses;
- stable identity (`occurrence_key`);
- relationship to Transactions / Commitments / Goals;
- domain invariants.

No application code in this slice — same mode as [Sprint 8.1](./sprint-8.1-planning-domain-model.md).

---

## Product principle

> Recurring events are expectations, not financial truth.  
> *Los movimientos recurrentes son expectativas, no hechos financieros.*

Codified as **[Principle 11](../product/02-product-principles.md)**. Protects P01 (Financial Truth) and P02 (One Source of Truth).

---

## Three concepts (never collapse)

```text
RecurringRule (template / configuration)
        ↓  generates under a bounded period
RecurringOccurrence (projected instance)
        ↓  only after explicit user confirmation
Transaction (fact on the ledger)
```

| Concept | Persisted? | Example |
|---------|------------|---------|
| **RecurringRule** | Yes | Internet · 800 MXN · monthly · day 15 |
| **RecurringOccurrence** | **No** (calculated) | Internet · 800 MXN · 15 Aug 2026 |
| **Transaction** | Yes | Cargo internet · 815 MXN · 16 Aug 2026 |

Date, amount, and status may all differ across the three. They are **not** the same entity.

---

## Aggregate: `RecurringRule`

**Technical name:** `RecurringRule`  
**Product name:** Movimiento recurrente

Conceptual fields (see RFC-005 for full shape):

- identity: `id`, `organization_id`, `version`
- money: `name`, `direction`, `amount` (expected), `currency`, `amount_strategy` (`fixed` \| `estimated`)
- certainty: `confirmed` \| `expected` \| `estimated` (feeds Planning inclusion)
- pattern: `RecurrencePattern` + `invalid_date_policy` (default `last_day_of_month`)
- validity: `starts_on`, `ends_on`
- accounts / category: `account_id`, `destination_account_id` (transfers), `category_id`
- provenance: `source_type` (`manual` \| `commitment` \| `goal` \| `tax` \| `system` \| `imported`), optional `related_resource_*`
- settlement: `settlement_mode` (V1 default `single_transaction`)
- lifecycle: `status` (`active` \| `paused` \| `ended` \| `archived`)
- optional: `grace_period_days`, `notes`

### Direction

`inflow` · `outflow` · `transfer`

Transfers are neither global income nor expense. V1: same currency only; `account_id ≠ destination_account_id`.

### Certainty ≠ amount strategy

| | Meaning |
|--|--|
| **Certainty** | How sure we are the event will happen (Planning inclusion) |
| **Amount strategy** | Whether `amount` is exact expectation (`fixed`) or reference (`estimated`) |

V1 stores a single `amount` for both strategies. No auto-average / min-max / statistical prediction yet.

---

## `RecurrencePattern` (immutable VO)

```text
frequency: daily | weekly | monthly | yearly
interval: int ≥ 1
days_of_week: for weekly
day_of_month / end_of_month: for monthly
month_of_year + day_of_month | end_of_month: for yearly
```

**Not** free-form RRULE as the domain interface (RRULE may be internal later).

### Invalid calendar dates (29 / 30 / 31)

`InvalidDatePolicy` persisted on the rule:

- **`last_day_of_month`** (default) — e.g. 31 → 28/29 Feb  
- **`skip_occurrence`** — omit months without that day  

### Out of V1 (model must still evolve)

Business days · nth weekday · special fortnight rules · bank calendars · holiday skips · arbitrary RRULE · complex times · combined intervals.

---

## Occurrences are projections

**Do not persist all future occurrences.** Persist:

```text
RecurringRule + Pauses + Exceptions + Transaction links
```

Generate on demand for `[period_start, period_end]` via a pure `RecurrenceGenerator`.

Never `generate_all_occurrences_forever()`. Defensive caps (e.g. max 366 days / 1000 occurrences per request) live in the API/use-case layer.

### Occurrence identity

```text
recurring:{rule_id}:occurrence:{YYYY-MM-DD}
```

Date in the key is **`original_expected_on`**. Rescheduling keeps the key; `expected_on` / `expected_at` may change.

Also carry:

- `expected_on: date` — financial intent (org timezone)  
- `expected_at: datetime` — technical ordering (local start-of-day default)

`next_occurrence` is always calculated — never a source of truth if cached.

### Occurrence statuses (derived)

`upcoming` · `due` · `overdue` · `settled` · `partially_settled` · `skipped` · `cancelled`

UX language: prefer **Pendiente de confirmar** over “vencida” for overdue forecasts — overdue ≠ contractual default.

---

## Pauses

`status = paused` alone loses history. Persist **`RecurringRulePause`** intervals (`starts_on` / `ends_on`).

- Pausing does not rewrite the past, delete exceptions, or touch transactions.  
- Occurrences inside pause windows are not generated.  
- Reactivation does **not** backfill skipped pause dates.

---

## Exceptions

`RecurringOccurrenceException` keyed by `original_occurrence_key`:

| Type (V1) | Effect |
|-----------|--------|
| `skip` | Exclude from active forecasts |
| `override` / `reschedule` / `amount_override` | Change date and/or amount (and optionally certainty) |

UI series actions for later slices: *Solo esta* (exception) · *Desde esta fecha* (effective versioning). Full structural history versioning (`recurring_rule_versions`) may wait; V1 must not silently rewrite settled history.

---

## Transactions — confirmation only

**Invariant:** Recurring never creates a Transaction without explicit user confirmation.

Allowed UX: “Registrar movimiento” / “Confirmar como ocurrió” → prefilled form → user confirms → Transaction + `source_occurrence_key` link → occurrence derives `settled`.

Matching levels: explicit create · manual link · suggested match (ask user; **no auto-settle in V1**).

Default settlement mode: **`single_transaction`** (linked tx settles even if amount differs; show delta). Cumulative mode reserved.

---

## Cross-module ownership

| `source_type` | Editable in Recurring UI? |
|---------------|---------------------------|
| `manual` | Yes |
| `commitment` / `goal` / `tax` | Show + deep-link; edit in owner module |

Planning dedupes via `occurrence_key` / explicit resource links (Commitment > Recurring when both represent the same payment — already in Sprint 8.3).

Calendar and Planning **must** consume the same generator — Calendar is not a second recurrence engine.

---

## Generator contract (preview for 9.2)

```text
generate(rule, period_start, period_end, pauses, exceptions)
  → tuple[RecurringOccurrence, ...]
```

Pure · deterministic · no repos · no wall clock · stable order.

Pipeline (locked for 9.2): validate → base dates → clip validity → invalid-date policy → exclude pauses → keys → exceptions → known settlements → status → sort.

---

## Aggregate invariants (summary)

1. `amount > 0`  
2. One currency per rule  
3. Transfer: two distinct org accounts, same currency (V1)  
4. `ends_on >= starts_on` when set  
5. `interval >= 1`  
6. Archived / ended rules do not generate  
7. Pauses exclude dates in their windows  
8. Exception touches one original occurrence; key stable under reschedule  
9. No auto Transaction  
10. An occurrence is never proof money moved  

Pattern field combinations validated inside the VO (daily/weekly/monthly/yearly rules in RFC-005).

---

## Acceptance criteria (9.1)

- [x] Formal separation: rule · occurrence · transaction  
- [x] `RecurringRule` is the aggregate; product name = Movimiento recurrente  
- [x] Frequencies: daily / weekly / monthly / yearly + interval  
- [x] Monthly: specific day + end-of-month; invalid-date policy explicit  
- [x] Generation always period-bounded; future occurrences not mass-persisted  
- [x] Deterministic `occurrence_key`; reschedule does not change identity  
- [x] Pauses do not rewrite history  
- [x] Exceptions can skip or override one occurrence  
- [x] Transfers: distinct same-currency accounts  
- [x] Real txs may link to occurrences; never auto-created  
- [x] Planning & Calendar share one generator surface  
- [x] Externally managed rules not freely editable in Recurring  
- [x] Engine designed as pure / testable without DB  

---

## Primary decision

**Do not persist `RecurringOccurrence` as a normal entity.**

Persistent truth:

```text
RecurringRule + Exceptions + Pauses + Transaction links
```

Occurrences are a **calculated projection** — same architectural shape as Planning:

```text
Persistent configuration  →  calculated result
```

---

## Next

**Sprint 9.2 — Generation engine** (next slice): algorithms for expanding daily/weekly/monthly/yearly rules, applying pauses/exceptions, and emitting stable keys.
