# Decision: Confirm recurring occurrence via explicit Transaction

**Date:** 2026-08-01  
**Status:** Accepted  
**Related:** [RFC-005](../rfc/RFC-005-recurring-engine.md) · [Sprint 9.4](../roadmap/sprint-9.4-recurring-ux.md) · Principle 11

---

## Context

Users need low-friction ways to mark that a recurring expectation happened, without turning forecasts into silent ledger posts.

## Decision

1. Nav label **Recurrentes** at `/app/recurring` (not “Suscripciones”).  
2. Overdue-style gaps use **Pendiente de confirmar**, not “Vencido”.  
3. Confirm opens the **Transactions** create flow (prefill + `source_occurrence_key`) — no Recurring-only post endpoint that bypasses the ledger.  
4. Even “Confirmar por $X” requires an explicit confirmation step.  
5. Amount variance settles the occurrence; updating future amounts is a **separate** version action.  
6. Unsaved and saved previews use the **same backend generator** — no FE date math.  
7. Calendar/Dashboard invoke Recurring commands; they do not own recurrence rules.

## Consequences

- Planning STS stays aligned with confirmed facts.  
- Transactions module remains source of truth for money movement.  
- 9.5 SPEC must cover deep-link/prefill contract and cache invalidation lists.
