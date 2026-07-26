# EPIC-006

# Financial Timeline

**Status:** Done  
**Parent:** [Module roadmap](../roadmap/module-roadmap.md), [RFC-003](../rfc/RFC-003-financial-timeline.md)  
**Depends on:** Accounts, Transactions, Dashboard, Goals, Financial Commitments (`v0.5.0-foundation` + SPEC-002)  
**Sprint:** [Sprint 7 — Financial Timeline](../roadmap/sprint-7-financial-timeline.md)  
**Decision:** [Financial Timeline](../decisions/2026-07-25-financial-timeline.md)

---

## Outcome

Users see **Historia** (Financial Timeline): a chronological spine of significant financial life events — not a technical activity log, not a second ledger.

```text
Transactions + Goals + Commitments → FinancialEvent → timeline_events → Historia
```

## Non-goals

- AI-generated Financial Story
- Export PDF/CSV, push notifications, bank import
- Reconstructing years of ledger on every read
- Writing Timeline from UI or ad-hoc SQL from other modules

## Notes

- Backend: `modules/timeline/` + contract in `shared/events/`  
- UI: `/app/timeline` · label **Historia**  
- **Build:** [SPEC-003](../../specs/backend/timeline/SPEC-003-financial-timeline.md)  
