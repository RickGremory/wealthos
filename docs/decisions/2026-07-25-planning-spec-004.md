# 2026-07-25 — Planning implementation via SPEC-004

**Type:** Process / execution  
**Status:** Accepted  
**Sprint:** [8.5](../roadmap/sprint-8.5-implementation-spec.md)  
**SPEC:** [SPEC-004](../../specs/backend/planning/SPEC-004-planning-safe-to-spend.md)

## Decision

Sprint 8 design (8.1–8.4) is **closed**. Implementation proceeds only through **SPEC-004** phases and PR plan. Persist only `planning_settings` and `planned_cash_flows`. Primary domain operation is `calculate_projection(context)`.

## Why

Keeps executable scope frozen (same pattern as SPEC-002 / SPEC-003) and prevents reopening product debates during coding.

## Consequences

- Recurring adapter may be empty until Sprint 9  
- No Timeline auto-events / projection snapshots in SPEC-004  
- Next product sprint after Planning ships: Recurring Engine  
