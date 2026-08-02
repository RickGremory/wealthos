# Sprint 9.2 — Recurrence Generation Engine

**Status:** Accepted  
**Parent:** [Sprint 9](./sprint-9-recurring-engine.md)  
**Contract:** [RFC-005](../rfc/RFC-005-recurring-engine.md)  
**Decision:** [Identity vs effective date](../decisions/2026-08-01-recurrence-identity-vs-effective-date.md)  
**Depends on:** [Sprint 9.1](./sprint-9.1-recurring-domain-model.md)

---

## Objective

Specify a **pure, deterministic** engine that turns one `RecurringRule` into concrete `RecurringOccurrence` values inside a requested period.

The engine must correctly handle:

- daily / weekly / monthly / yearly frequencies and intervals;
- `starts_on` / inclusive `ends_on`;
- short months and leap years;
- pause windows and exceptions;
- stable occurrence keys;
- defensive range/count limits;
- chronological stable order;
- status from an explicit `evaluated_on`.

It does **not** query the database, create transactions, or mutate rules.

No production module code in this slice — algorithms + contracts + test matrix only (same mode as 9.1 / 8.2).

---

## Primary contract

```python
class RecurrenceGenerator(Protocol):
    def generate(
        self,
        *,
        rule: RecurringRule,
        period_start: date,
        period_end: date,
        pauses: Sequence[RecurringRulePause] = (),
        exceptions: Sequence[RecurringOccurrenceException] = (),
        settlements: Sequence[RecurringOccurrenceSettlement] = (),
        evaluated_on: date,
        timezone: str,
    ) -> tuple[RecurringOccurrence, ...]:
        ...
```

| Input | Role |
|-------|------|
| `rule` | Persistent configuration (one effective version) |
| `period_start` / `period_end` | Inclusive requested window |
| `pauses` / `exceptions` / `settlements` | Injected context (no repos inside the engine) |
| `evaluated_on` | Explicit “today” for due / overdue — never `date.today()` |
| `timezone` | Org zone for `expected_at` |

Output: immutable, chronologically ordered tuple.

### Request invariants

```text
period_start <= period_end
(period_end - period_start).days + 1 <= MAX_GENERATION_DAYS   # 366
len(result) <= MAX_OCCURRENCES_PER_REQUEST                    # 1000
```

Violations raise (no silent truncation):

- `InvalidRecurrenceRange`
- `RecurrenceRangeTooLarge`
- `RecurrenceOccurrenceLimitExceeded`

---

## Strategy split

```text
DefaultRecurrenceGenerator
├── DailyRecurrenceStrategy
├── WeeklyRecurrenceStrategy
├── MonthlyRecurrenceStrategy
└── YearlyRecurrenceStrategy
```

```python
class RecurrenceStrategy(Protocol):
    def generate_base_dates(
        self,
        *,
        rule: RecurringRule,
        effective_start: date,
        effective_end: date,
    ) -> tuple[date, ...]:
        ...
```

Strategies emit **base dates only**. The orchestrator owns validity intersection, pauses, keys, exceptions, `expected_at`, status, ordering, and limits.

---

## Pipeline

1. Validate request + rule pattern  
2. Resolve effective range (period ∩ rule validity ∩ status)  
3. Select strategy → base dates  
4. Build original occurrence keys  
5. Drop dates inside normalized pauses (**on base date**)  
6. Apply exceptions (skip / reschedule / amount / override)  
7. Pull **moved-into-range** exceptions whose base is outside the window  
8. Build drafts → attach settlements → resolve status  
9. Filter by **effective** `expected_on` ∈ `[period_start, period_end]`  
10. Stable sort → enforce count limit → return  

### Effective range

```text
effective_start = max(period_start, rule.starts_on)
effective_end   = min(period_end, rule.ends_on or period_end)
```

If `effective_start > effective_end` → `()`.

If `rule.status ∈ {ARCHIVED, ENDED}` → `()`.

`PAUSED` alone does **not** empty the result — open/closed pause intervals do.

`ends_on` is **inclusive**.

---

## Identity vs effective date

| Concept | Field | Drives |
|---------|-------|--------|
| Base / identity | `original_expected_on` | `occurrence_key` |
| Effective expectation | `expected_on` | Planning / Calendar filter & display |

```text
original_expected_on  →  identity
expected_on           →  current expected execution date
```

Reschedule may change `expected_on` without changing the key.

```python
OccurrenceKey.for_recurring_rule(rule_id, original_date)
# recurring:{uuid}:occurrence:YYYY-MM-DD
```

Key must **not** include amount, name, category, rescheduled date, version id, or timezone.

---

## Anchoring (all frequencies)

Every sequence anchors to `rule.starts_on` — never to `period_start` or “today”.

Jump forward with arithmetic (day/week/month/year index); **do not** walk from a decade-old `starts_on` day by day.

Generated base dates must satisfy `candidate >= starts_on` and `candidate <= ends_on` (when set).

---

## Daily

`first_daily_occurrence_on_or_after(anchor, target, interval)` via modulo on elapsed days, then step by `interval`.

Example: start 1 Aug, every 5 days, query 8–25 Aug → **11, 16, 21** (not a new sequence from the 8th).

---

## Weekly

- Technical week starts **Monday** (`weekday()` / `Weekday` IntEnum 0–6).  
- `days_of_week` normalized: unique, sorted, ≥1.  
- Week participates when `(weeks_since_anchor_week) % interval == 0`.  
- Skip candidates before `starts_on`.

“Biweekly” is `weekly` + `interval=2` — not a separate product frequency named quincenal inside the engine.

Example: weekly Mon+Thu, `starts_on` Wed 5 Aug → first hit **Thu 6 Aug**, then Mon 10, …

---

## Monthly

- Exactly one of `day_of_month` or `end_of_month`.  
- Month index: `year * 12 + month - 1`; advance with `add_months` — **never** `+timedelta(days=30)`.  
- Eligible months: `(month_index - anchor_month_index) % interval == 0`.  
- Resolve day each month from the **original** pattern (31 Jan → Feb adjusted → March requests 31 again).  

`InvalidDatePolicy`:

| Policy | Missing day N |
|--------|----------------|
| `last_day_of_month` (default) | Clamp to last day |
| `skip_occurrence` | Omit that month |

Quarterly example: start 10 Feb, interval 3 → Feb / May / Aug / Nov.

If `starts_on` is after the pattern day in that month (monthly day 5, start 20 Aug), first occurrence is **5 Sep**.

---

## Yearly

- Anchor on `starts_on.year`; year participates when `(year - starts_on.year) % interval == 0`.  
- Requires `month_of_year` + (`day_of_month` or `end_of_month`).  
- Reuse monthly day resolution + same invalid-date policy (29 Feb leap / non-leap).

---

## Pauses

Normalize before apply: same rule, sort by `starts_on`, merge overlapping/adjacent intervals. Open pause (`ends_on is None`) excludes from `starts_on` forward.

**Order:** base date → pause check → exception.

A pause on the **original** date still omits the occurrence even if a reschedule would move it outside the pause window (V1: no “reactivate paused occurrence” exception).

---

## Exceptions

Index by `original_occurrence_key` — at most one active exception per key.

| Type | Effect |
|------|--------|
| `SKIP` | Status `skipped`; still returned by engine; Planning filters out |
| `RESCHEDULE` | New `expected_on`; key unchanged |
| `AMOUNT_OVERRIDE` | `expected_amount` override; expose `base_amount` + `expected_amount` |
| `OVERRIDE` | Date and/or amount and/or certainty |

Not overridable via exception: direction, currency, accounts, owner resource link.

### Reschedule across period boundaries

Filter consumers by **effective** date. Repository / use-case must load exceptions that affect the period:

```text
original_expected_on ∈ range
OR replacement_expected_on ∈ range
```

so a move from 15 Aug → 2 Sep appears in a September query.

Two different keys may share the same effective date (Aug moved to 15 Sep + natural Sep 15) — **do not merge**; optional advisory `multiple_occurrences_same_effective_date`.

---

## `expected_at`

```text
datetime.combine(expected_on, time.min, tzinfo=ZoneInfo(timezone))
```

UI and financial meaning prefer `expected_on`. UTC offset shifts must not rewrite the calendar day of intent.

---

## Status resolution

Priority: `skipped` → `cancelled` → `settled` / `partially_settled` → date-based (`upcoming` / `due` / `overdue`).

| Mode | Rule |
|------|------|
| `single_transaction` | Any explicit link → `settled` (amount variance shown, not partial) |
| `cumulative` | Sum linked amounts vs expected → none / partial / settled |

Grace: `expected_on … expected_on + grace_period_days` → `due`; after → `overdue`. With `grace_period_days = 0`, expected day is `due`, next day `overdue`. Product UX may label overdue as **Pendiente de confirmar**.

---

## Ordering

```text
(expected_on, occurrence_key)
```

Never name or amount.

---

## Pureza

Same inputs ⇒ identical output. Forbidden inside the engine: `date.today()`, `datetime.now()`, repository I/O.

Rule **version selection** is a higher service (`RecurringRuleVersionResolver`); 9.2 strategies receive one non-overlapping version slice. Version id is **not** part of the occurrence key.

---

## Consumers

| Consumer | Behavior |
|----------|----------|
| **Planning** | Call app service → generator → drop `skipped`/`cancelled` → `PlanningCashFlow` (keep key). No re-expansion. |
| **Calendar** | Same occurrences; may show skipped muted; no private monthly math. |

Target: ≤ 1000 occurrences in &lt; ~50 ms for the pure engine under normal fixtures (indexed exceptions/settlements).

---

## Domain errors (stable codes)

`RecurrenceError` and subclasses: `InvalidRecurrenceRange`, `RecurrenceRangeTooLarge`, `RecurrenceOccurrenceLimitExceeded`, `UnsupportedRecurrenceFrequency`, `InvalidRecurrencePattern`, `InvalidOccurrenceException`, `DuplicateOccurrenceException`, `InvalidPausePeriod`, `UnsupportedInvalidDatePolicy`.

---

## Essential test matrix

**Daily / weekly / monthly / yearly** — anchors, intervals, mid-period start, year boundaries, `ends_on` inclusive, invalid-day policies, leap 29 Feb.

**Pauses** — cover / miss / merge / open / resume / reschedule-out still omitted.

**Exceptions** — skip, amount, in/out reschedule, moved-into-range, stable key, same effective date two keys, duplicate key, wrong rule, invalid amount.

**Status** — upcoming / due / grace / overdue / skipped / settled (single + variance) / partial cumulative — all with explicit `evaluated_on`.

**Property (Hypothesis)** — ordered; effective dates in range; unique keys; deterministic; base dates within validity; daily spacing multiple of interval; monthly respects pattern or policy.

---

## Acceptance criteria (9.2)

- [x] Pure generator contract with injected context and `evaluated_on`  
- [x] Separate daily / weekly / monthly / yearly strategies  
- [x] All intervals anchored on `starts_on`; no 30-day month hacks  
- [x] Jump-ahead first occurrence (no decade walk)  
- [x] Day 29/30/31 + leap years honor persisted policy  
- [x] Inclusive `ends_on`; archived/ended empty; pauses on base date  
- [x] Exception keeps identity; moved-into-range supported; no date-merge of distinct keys  
- [x] single + cumulative settlement modes specified  
- [x] Range/count limits fail loud  
- [x] Planning & Calendar share one engine  
- [x] Parametrized + property-test matrix defined  

*(Checklist locked as design acceptance; code lands in 9.5 / SPEC.)*

---

## Main decision of 9.2

Keep **identity date** and **expected execution date** separate so reschedule never breaks links, Traceability, or Planning dedupe.

## Next

**Sprint 9.3 — Persistence, commands, lifecycle:** tables, create/edit, pauses, exceptions, effective versioning, archive, backend APIs, replace Planning stub wiring.
