# Decision: Recurrence identity date vs effective date

**Date:** 2026-08-01  
**Status:** Accepted  
**Related:** [RFC-005](../rfc/RFC-005-recurring-engine.md) · [Sprint 9.2](../roadmap/sprint-9.2-recurrence-generation.md)

---

## Context

Sprint 9.1 defined projected occurrences and stable keys. Generation must support reschedule, pauses, and period queries without rewriting identity or inventing a second calendar engine.

## Decision

1. **`original_expected_on`** (base pattern date) owns the `occurrence_key`.  
2. **`expected_on`** is the current expected execution date after exceptions.  
3. The generator is **pure**: no DB, no `date.today()`, no auto Transactions.  
4. **Pauses apply to the base date** before exceptions; V1 does not let a reschedule escape a pause.  
5. Consumers filter by **effective** date; exception loading must include originals **or** replacements that intersect the period.  
6. Distinct keys on the same effective day are **not** merged.  
7. Frequency strategies only emit base dates; orchestration owns the rest.  
8. Limits (`MAX_GENERATION_DAYS=366`, `MAX_OCCURRENCES_PER_REQUEST=1000`) raise — never silent truncate.

## Consequences

- Planning/Calendar share one expansion path.  
- Settlement links remain valid after single-occurrence reschedule.  
- Persistence (9.3) must expose `list_affecting_period` for exceptions.  
- Implementation (9.5) starts from parametrized + Hypothesis tests against this contract.
