# 2026-07-25 — Planning adapters and occurrence_key

**Type:** Architecture / integration  
**Status:** Accepted  
**Sprint:** [8.3](../roadmap/sprint-8.3-planning-integration.md)  
**Parent:** [RFC-004](../rfc/RFC-004-planning-projection.md) · [8.2 algorithm](../roadmap/sprint-8.2-safe-to-spend-algorithm.md)

## Decision

Planning integrates with other modules exclusively through **adapters** that emit normalized contracts (`PlanningAccountSnapshot`, `PlanningCashFlow`, `PlanningReservation`, `PlanningSettlement`) keyed by stable **`occurrence_key`**.

The projection engine never imports foreign SQLAlchemy models or joins foreign tables. Dashboard never reimplements Safe To Spend math.

## Why

Heterogeneous modules must feed one deterministic engine without double-counting or leaking domain internals. Explicit occurrence identity beats heuristic matching for partial payments and shifted dates.

## Consequences

- Read ports live at module boundaries; adapters preferably under owning modules  
- Transactions should carry `planning_occurrence_key` when created from commitment/recurring/goal/tax/manual plan  
- Deduplicate before settlement reconcile  
- Calendar is a view, not a source  
- Timeline emissions deferred past V1 on-demand calc  
