# Sprint 7 — Financial Timeline

**Epic:** [EPIC-006](../epics/EPIC-006-timeline.md)  
**RFC:** [RFC-003](../rfc/RFC-003-financial-timeline.md)  
**SPEC:** [SPEC-003](../../specs/backend/timeline/SPEC-003-financial-timeline.md)  
**Decision:** [2026-07-25 Financial Timeline](../decisions/2026-07-25-financial-timeline.md)

## Intent

Ship the Financial Timeline as WealthOS’s narrative glue: contract, persistence, publishers, API, Historia UI, and Dashboard recent feed.

## Product UI

| Concept | Value |
|---------|-------|
| Route | `/app/timeline` |
| Nav label | **Historia** |
| Question | ¿Qué ha pasado en mi vida financiera? |

## Phases (SPEC-003)

1. Persistence — `timeline_events` + model/repo  
2. Contract + publisher/projector  
3. Publishers — transactions + commitments  
4. API list + tests  
5. Frontend Historia  
6. Dashboard feed + goals publishers  
7. Quality — E2E smoke, seed, OpenAPI, SPEC Completed  

## Explicit out of scope

AI Financial Story · PDF/CSV · push · bank import · Kafka/outbox
