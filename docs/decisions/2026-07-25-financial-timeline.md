# 2026-07-25 — Financial Timeline

**Type:** Product  
**Status:** Accepted (implemented via [SPEC-003](../../specs/backend/timeline/SPEC-003-financial-timeline.md) Completed)  
**Sprint:** [Sprint 7 — Financial Timeline](../roadmap/sprint-7-financial-timeline.md)  
**Prior:** Concept reserved during [6.3 Integration](../roadmap/sprint-6.3-commitments-integration.md)

## Decision

Introduce **Financial Timeline** as a WealthOS signature concept: a unified chronological view of the user’s financial life.

It is **not**:

- A new ledger  
- A social activity feed  
- A replacement for module-specific detail screens  

It **is** a composition surface over coherent events from Transactions, Goals, Financial Commitments, Calendar, Taxes, and Planning.

## Why

Per-module histories fragment the story. A single timeline turns WealthOS into a narrative of financial progress — highly differentiated vs expense trackers.

## Consequences (now)

- Modules publish `FinancialEvent` via `shared/events/`; only `modules/timeline/` projects to `timeline_events`.  
- Product UI: `/app/timeline`, nav **Historia**.  
- Bus MVP: sync in-process publisher (same signature for a future real bus).  
- AI Financial Story remains out of Sprint 7 (M7+).

## Later

AI coaching context, richer grouping, planning/tax publishers beyond stubs.
