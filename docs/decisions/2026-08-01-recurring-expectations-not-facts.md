# Decision: Recurring events are expectations, not financial truth

**Date:** 2026-08-01  
**Status:** Accepted  
**Related:** [RFC-005](../rfc/RFC-005-recurring-engine.md) · [Sprint 9.1](../roadmap/sprint-9.1-recurring-domain-model.md) · [Principle 11](../product/02-product-principles.md)

---

## Context

Planning (Sprint 8) treats Recurring as a forecast source and already defined:

```text
recurring:{id}:occurrence:{date}
```

We must model recurrence without inventing a second ledger or auto-posting transactions.

## Decision

1. **Three concepts:** `RecurringRule` (persisted) → `RecurringOccurrence` (calculated) → `Transaction` (fact).  
2. **Do not mass-persist future occurrences.** Persist rules, pauses, exceptions, and transaction links.  
3. **Never auto-create Transactions** from recurrence; confirmation is mandatory.  
4. **Occurrence keys stay stable** under single-occurrence reschedule (`original_expected_on` in the key).  
5. **Default invalid-date policy:** `last_day_of_month`, persisted on the rule.  
6. **Pauses are intervals**, not only a boolean status.  
7. Product principle **P11** records: *Recurring events are expectations, not financial truth.*

## Consequences

- Planning adapter can replace the Sprint 8 stub with real expansions without changing STS math.  
- Calendar must reuse the same generator.  
- Editing structural series history needs an effective-from strategy (full versioning table can wait; no silent rewrite of settled keys).  
- Next design slice: **9.2** generation algorithms → **Accepted** ([Sprint 9.2](../roadmap/sprint-9.2-recurrence-generation.md)).
