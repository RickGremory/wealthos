# SPEC-003

# Financial Timeline — End-to-End Implementation

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Author** | Ricardo Balam |
| **Created** | 2026-07-25 |
| **Parent Epic** | [EPIC-006](../../../docs/epics/EPIC-006-timeline.md) |
| **Parent RFC** | [RFC-003](../../../docs/rfc/RFC-003-financial-timeline.md) |
| **Sprint brief** | [Sprint 7](../../../docs/roadmap/sprint-7-financial-timeline.md) |

> Once **Completed**, this SPEC is immutable. Further changes require a new SPEC.

---

## 1. Objective

Ship Financial Timeline end-to-end so a user can:

1. See significant financial events in chronological order (Historia)  
2. Filter by source, importance, currency, and date range  
3. Deep-link from an event to its original resource  
4. See Dashboard “actividad reciente” fed from Timeline (`importance ≥ high`)  

Without recalculating years of ledger or summing cross-currency amounts.

---

## 2. Scope

### Included

- Table `timeline_events` + Alembic migration  
- `shared/events.FinancialEvent`  
- In-process `EventPublisher` + `TimelineProjector`  
- Publishers: transactions, debts/commitments, goals  
- `GET /api/v1/organizations/{org_id}/timeline` (cursor pagination + filters)  
- UI `/app/timeline` + nav **Historia**  
- Dashboard activity from Timeline  
- Seed demo emits events; OpenAPI regenerated; tests  

### Out of scope

- AI story, exports, push, bank import, Kafka/outbox  
- Aggressive multi-event clustering beyond a simple optional 30s rule  

---

## 3. Architecture

```text
UI Historia (/app/timeline) + Dashboard activity
        │
        ▼
GET /organizations/{id}/timeline
        │
        ▼
modules/timeline/  (projection + queries)
        ▲
        │ FinancialEvent
shared/events/
        ▲
publishers in transactions / debts / goals
```

**Invariants:** publishers only · org isolation · no cross-currency sums · importance filter · human copy ES in title/description.

---

## 4. Persistence

`timeline_events`: id, organization_id, occurred_at, source_type, event_type, importance, title, description, resource_type, resource_id, currency, amount, metadata (JSONB), created_at.

Indexes: `(organization_id, occurred_at DESC)`, `(organization_id, source_type, occurred_at DESC)`, unique `(organization_id, source_type, event_type, resource_id, occurred_at)` for publisher idempotency.

---

## 5. Phases / DoD checklist

| Phase | Deliverable | Done when |
|-------|-------------|-----------|
| 1 | Persistence | Migration + model + repo |
| 2 | Contract + bus | FinancialEvent + publisher/projector |
| 3 | Publishers tx + commitments | Events after write commands |
| 4 | API | Paginated GET + tests |
| 5 | Frontend | Historia page + nav |
| 6 | Dashboard + goals | Feed + goal publishers + seed |
| 7 | Quality | E2E smoke, OpenAPI, SPEC → Completed |

---

## 6. Acceptance criteria

- Modules publish via common contract (no cross inserts)  
- Timeline shows significant events only (not note/name edits)  
- Events deep-link to original resources  
- Dashboard reuses Timeline for recent activity  
- Paginated, ordered, tenant-isolated  
- No global cross-currency totals  
- Semantic fields suitable as future AI context  
