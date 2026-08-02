# 2026-08-01 — Recurring implementation via SPEC-005

**Type:** Process / execution  
**Status:** Accepted  
**Sprint:** [9.5](../roadmap/sprint-9.5-implementation-spec.md)  
**SPEC:** [SPEC-005](../../specs/backend/recurring/SPEC-005-recurring-engine.md)

## Decision

Sprint 9 design (9.1–9.4) is **closed**. Implementation proceeds only through **SPEC-005** phases and PR plan.

Additionally lock:

1. Fifth table **`recurring_occurrence_settlements`** as Recurring’s settlement source of truth (with optional Transaction source pointer).  
2. Atomic confirm: Transaction create + settlement in one monolith transaction when source is explicit.  
3. V1 no retroactive structural `effective_from` before org-local today.  
4. Resume semantics: `ends_on = resume_on - 1 day`.  
5. Planning adapter excludes externally managed rules (owner module owns cash-flow emission).

## Why

Same freeze pattern as SPEC-002–004; keeps coding from reopening product debates and prevents expectation/fact fusion.

## Consequences

- Coding may start on PR 1 without reopening 9.1–9.4  
- Next product design after Recurring ships: **Sprint 10 — AI Financial Assistant Foundation**  
- SPEC status moves Ready → Completed when phase 9 DoD is met  

## Outcome

SPEC-005 marked **Completed** after PR9 (perms aliases, timeline/audit/metrics, role tests, Playwright smoke).