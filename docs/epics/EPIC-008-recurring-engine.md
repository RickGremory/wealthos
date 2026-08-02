# EPIC-008

# Recurring Engine

**Status:** In progress (9.1 Accepted)  
**Parent:** [Module roadmap](../roadmap/module-roadmap.md), [RFC-005](../rfc/RFC-005-recurring-engine.md)  
**Depends on:** Accounts, Transactions, Planning (occurrence_key contract), Commitments, Goals  
**Sprint:** [Sprint 9 — Recurring Engine](../roadmap/sprint-9-recurring-engine.md)  
**Decision:** [Recurring = expectations, not facts](../decisions/2026-08-01-recurring-expectations-not-facts.md)

---

## Outcome

Users can define **Movimientos recurrentes** that expand into dated forecasts for Planning and Calendar, and can **confirm** an occurrence into a real Transaction — without cron jobs inventing ledger rows.

## Non-goals

- Auto-posting transactions  
- Free-form RRULE as primary UX  
- Bank / Open Banking sync  
- FX multi-currency transfers  

## Notes

- New module: `modules/recurring/`  
- Replaces Planning’s empty Recurring adapter from Sprint 8  
- **9.1** Domain model — **Accepted** ([RFC-005](../rfc/RFC-005-recurring-engine.md))  
- **9.2** Generation engine — Planned  
- **9.3** Persistence + API + Planning adapter — Planned  
- **9.4** UX — Planned  
- **9.5** SPEC + implementation — Planned  
