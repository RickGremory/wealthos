# Sprint 9.5 — Technical SPEC & Implementation Plan

**Status:** Accepted (design closed — execution via [SPEC-005](../../specs/backend/recurring/SPEC-005-recurring-engine.md))  
**Parent:** [Sprint 9](./sprint-9-recurring-engine.md)  
**Contracts:** [9.1](./sprint-9.1-recurring-domain-model.md) · [9.2](./sprint-9.2-recurrence-generation.md) · [9.3](./sprint-9.3-persistence-lifecycle.md) · [9.4](./sprint-9.4-recurring-ux.md)

> Day-to-day coding follows **SPEC-005**. Do not reopen 9.1–9.4 for implementation details.

---

## Objective

Turn 9.1–9.4 into an executable plan so Recurring ships end-to-end:

```text
Create rule → generate occurrences → Planning/Calendar consume
→ user confirms → Transaction created → occurrence settled
→ Planning stops forecasting it → Dashboard/Timeline update
```

## End-to-end guarantee

Three levels stay distinct forever:

| Layer | Role |
|-------|------|
| `RecurringRule` (+ versions) | Repetitive **intention** |
| `RecurringOccurrence` | Projected **expectation** |
| `Transaction` | Proven **fact** |

## Out of scope (still)

Auto-create transactions · bank detection · heuristic matching · FX · business days/holidays · free RRULE · push/email · statistical amount prediction · mass-persist future occurrences

## PR plan (summary)

| PR | Focus |
|----|--------|
| 1 | Persistence foundation (5 tables + Alembic + repos) |
| 2 | Pure recurrence engine + property tests |
| 3 | Lifecycle commands + optimistic lock |
| 4 | Read APIs (list, detail, preview, occurrences) |
| 5 | Settlements + Transactions integration + void |
| 6 | Planning / Calendar / Dashboard adapters |
| 7 | Frontend overview |
| 8 | Frontend forms + confirm / skip / version |
| 9 | Hardening (perms, audit, observability, E2E) |

## Next after Sprint 9

[Sprint 10 — AI Financial Assistant Foundation](./sprint-10-ai-foundation.md) (when opened) — permissions, data minimization, tools, traceability, explanation limits — **before** chatbots or recommendations.
