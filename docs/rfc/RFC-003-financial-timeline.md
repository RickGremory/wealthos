# RFC-003

# Financial Timeline — Narrative Event Spine

**Author:** Ricardo Balam  
**Status:** Accepted  
**Created:** 2026-07-25  
**Sprint:** Sprint 7 — Financial Timeline  
**Baseline:** post–SPEC-002 (Financial Commitments)

> **Frozen as product/architecture contract.** Execution via [EPIC-006](../epics/EPIC-006-timeline.md) and [SPEC-003](../../specs/backend/timeline/SPEC-003-financial-timeline.md).  
> See [PRODUCT_LANGUAGE.md](../product/PRODUCT_LANGUAGE.md) and [decision](../decisions/2026-07-25-financial-timeline.md).

---

## Summary

WealthOS unifies significant domain events into a **Financial Timeline**: a human-readable chronological story of financial life.

Modules publish a common `FinancialEvent` contract. The Timeline module projects those events into `timeline_events`. The UI (**Historia**) and Dashboard recent feed consume the projection — never inventing inserts from the client.

```text
Modules (transactions | goals | debts | …)
        │
        ▼
shared/events.FinancialEvent
        │
        ▼
EventPublisher (in-process, sync)
        │
        ▼
TimelineProjector → timeline_events
        │
        ├──► GET /timeline  →  /app/timeline (Historia)
        └──► Dashboard activity (importance ≥ high)
```

---

## Motivation

Per-module histories fragment the story. After Commitments, the next differentiator is narrative clarity: *¿Qué ha pasado en mi vida financiera?*

---

## Goals

- Persist only **significant** events (importance `normal+` in the main feed; `low` excluded)
- One contract for all producers
- Tenant-isolated, cursor-paginated API
- Currency Integrity (P09): filterable by currency; never sum cross-currency
- Deep-link to original resources
- Shape ready for future AI coaching context (semantic fields, not raw ledger dump)

## Non-goals (Sprint 7)

- Kafka / outbox / async bus (keep sync in-process with the same publish signature)
- AI Financial Story, PDF/CSV export, push, bank import
- Ultra-aggressive multi-event grouping (optional simple 30s rule only)
- Planning/tax full publishers (stubs OK; do not block)

---

## Design decisions

| Decision | Choice |
|----------|--------|
| Persistence | Projected `timeline_events` table — no full ledger replay |
| Contract location | `shared/events/` |
| Module | `modules/timeline/` |
| Bus MVP | Sync in-process after successful write boundary |
| Writers | Publishers from modules only |
| Readers | Any org member |
| UI | `/app/timeline`, nav **Historia** |

### `FinancialEvent` fields

`id`, `organization_id`, `occurred_at`, `source_type`, `event_type`, `importance`, `title`, `description`, `resource_type`, `resource_id`, optional `currency` / `amount` / `metadata`.

`source_type`: `transaction | goal | commitment | planning | tax | system`  
`importance`: `low | normal | high | critical`

### Importance MVP

- Transactions: income → high; liability transfer / commitment payment → high; material expense → normal; micro → low (not projected)
- Goals: create / milestones 25–100 / completed → high
- Commitments: create, payment, overdue (once), closed/paid_off → high/critical

---

## Success criteria

- No cross-module SQL inserts into `timeline_events`
- Feed significant-only, ordered, paginated, tenant-safe
- Dashboard recent activity from Timeline
- P09 respected
- OpenAPI + tests + seed emit events
