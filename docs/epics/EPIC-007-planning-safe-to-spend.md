# EPIC-007

# Planning & Safe To Spend

**Status:** In progress (8.1 Accepted)  
**Parent:** [Module roadmap](../roadmap/module-roadmap.md), [RFC-004](../rfc/RFC-004-planning-projection.md)  
**Depends on:** Accounts, Transactions, Commitments, Goals, Taxes, Timeline  
**Sprint:** [Sprint 8 — Planning & Safe To Spend](../roadmap/sprint-8-planning-safe-to-spend.md)  
**Decision:** [Safe To Spend as Financial Projection](../decisions/2026-07-25-safe-to-spend-projection.md)

---

## Outcome

Users see **Disponible para gastar** as an explained Financial Projection — not a raw balance — answering:

> ¿Cuánto dinero puedo usar hoy sin comprometer metas ni obligaciones?

## Non-goals

- AI coaching (consumes this later)  
- Bank import / Open Banking  
- Year-long projections  
- Planning mutating the ledger  

## Notes

- Backend: elevate `modules/planning/` around `PlanningProjection` + policies  
- UI: Planning surfaces + Dashboard Safe To Spend as star widget  
- **8.1** Domain model — **Accepted** ([RFC-004](../rfc/RFC-004-planning-projection.md))  
- **8.2–8.5** follow in sprint brief  
