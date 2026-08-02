# Sprint 9 — Recurring Engine

**Status:** Design in progress (9.1–9.2 Accepted)  
**Epic:** [EPIC-008](../epics/EPIC-008-recurring-engine.md)  
**RFC:** [RFC-005](../rfc/RFC-005-recurring-engine.md)  
**Decision:** [Recurring = expectations, not facts](../decisions/2026-08-01-recurring-expectations-not-facts.md) · [Identity vs effective date](../decisions/2026-08-01-recurrence-identity-vs-effective-date.md)

---

## Product rule

> Una regla recurrente predice movimientos; nunca demuestra que ocurrieron.

```text
Recurring Rule  →  Forecast
Transaction     →  Fact
```

This keeps Planning’s Facts vs Forecasts intact and protects **P01 / P02** (transactions remain the only ledger truth).

---

## Design pillars

| Slice | Focus | Status |
|-------|--------|--------|
| **9.1** | Domain model (rule, occurrence, exceptions, keys) | **Accepted** — [9.1](./sprint-9.1-recurring-domain-model.md) |
| **9.2** | Generation engine (daily / weekly / monthly / yearly) | **Accepted** — [9.2](./sprint-9.2-recurrence-generation.md) |
| **9.3** | Persistence, API, Planning adapter (replace stub) | Planned |
| **9.4** | UX — Movimientos recurrentes + confirm flow | Planned |
| **9.5** | SPEC + implementation | Planned |

Day-to-day coding follows a SPEC once 9.5 opens. Do not reopen 9.2 for tables/API — that is **9.3**.

---

## Why after Planning

Sprint 8 shipped Safe To Spend with a **Recurring adapter stub**. Sprint 9 fills that forecast source without auto-creating ledger rows.

## Out of scope (Sprint 9)

AI prediction · bank sync · business-day calendars · free-form RRULE UI · auto-create transactions · FX transfers · probabilistic amounts

## Related

[Principle 11](../product/02-product-principles.md) · [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md) · [Sprint 8.3 occurrence_key](./sprint-8.3-planning-integration.md)
