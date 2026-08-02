# EPIC-008

# Recurring Engine

**Status:** In progress (9.1–9.4 Accepted)  
**Parent:** [Module roadmap](../roadmap/module-roadmap.md), [RFC-005](../rfc/RFC-005-recurring-engine.md)  
**Depends on:** Accounts, Transactions, Planning (occurrence_key contract), Commitments, Goals  
**Sprint:** [Sprint 9 — Recurring Engine](../roadmap/sprint-9-recurring-engine.md)  
**Decisions:** [Expectations ≠ facts](../decisions/2026-08-01-recurring-expectations-not-facts.md) · [Identity vs effective date](../decisions/2026-08-01-recurrence-identity-vs-effective-date.md) · [Rule + Version](../decisions/2026-08-01-recurring-rule-versioning.md) · [Confirm via Transaction](../decisions/2026-08-01-recurring-confirm-occurrence.md)

---

## Outcome

Users can define **Movimientos recurrentes** (**Recurrentes**) that expand into dated forecasts for Planning and Calendar, and can **confirm** an occurrence into a real Transaction — without cron jobs inventing ledger rows.

## Non-goals

- Auto-posting transactions  
- Free-form RRULE as primary UX  
- Bank / Open Banking sync  
- FX multi-currency transfers  

## Notes

- New module: `modules/recurring/` · UI `/app/recurring`  
- Replaces Planning’s empty Recurring adapter from Sprint 8  
- **9.1** Domain model — **Accepted**  
- **9.2** Generation engine — **Accepted**  
- **9.3** Persistence + commands + Planning port — **Accepted**  
- **9.4** UX + confirmation — **Accepted** ([Sprint 9.4](../roadmap/sprint-9.4-recurring-ux.md))  
- **9.5** SPEC + implementation — Planned  
