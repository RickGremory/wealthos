# Sprint 9 — Recurring Engine

**Status:** Design complete (9.1–9.5 Accepted) · Implementation via [SPEC-005](../../specs/backend/recurring/SPEC-005-recurring-engine.md) (**Ready**)  
**Epic:** [EPIC-008](../epics/EPIC-008-recurring-engine.md)  
**RFC:** [RFC-005](../rfc/RFC-005-recurring-engine.md)

**Decisions:** [Expectations ≠ facts](../decisions/2026-08-01-recurring-expectations-not-facts.md) · [Identity vs effective date](../decisions/2026-08-01-recurrence-identity-vs-effective-date.md) · [Rule + Version](../decisions/2026-08-01-recurring-rule-versioning.md) · [Confirm via Transaction](../decisions/2026-08-01-recurring-confirm-occurrence.md) · [SPEC-005](../decisions/2026-08-01-recurring-spec-005.md)

---

## Product rule

> Una regla recurrente predice movimientos; nunca demuestra que ocurrieron.

```text
Recurring Rule  →  Forecast
Transaction     →  Fact
```

---

## Design pillars

| Slice | Focus | Status |
|-------|--------|--------|
| **9.1** | Domain model | **Accepted** — [9.1](./sprint-9.1-recurring-domain-model.md) |
| **9.2** | Generation engine | **Accepted** — [9.2](./sprint-9.2-recurrence-generation.md) |
| **9.3** | Persistence & lifecycle | **Accepted** — [9.3](./sprint-9.3-persistence-lifecycle.md) |
| **9.4** | UX + confirmation | **Accepted** — [9.4](./sprint-9.4-recurring-ux.md) |
| **9.5** | SPEC + PR plan | **Accepted** — [9.5](./sprint-9.5-implementation-spec.md) · [SPEC-005](../../specs/backend/recurring/SPEC-005-recurring-engine.md) Ready |

Coding follows **SPEC-005** only. Do not reopen 9.1–9.4 during implementation.

---

## Out of scope

AI prediction · bank sync · business-day calendars · free-form RRULE UI · auto-create transactions · FX · probabilistic amounts · mass-persist occurrences

## After ship

[Sprint 10 — AI Foundation](./sprint-10-ai-foundation.md) (placeholder).

## Related

[Principle 11](../product/02-product-principles.md) · [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md)
