# EPIC-005

# Financial Commitments — Debt

**Status:** In progress  
**Parent:** [Module roadmap](../roadmap/module-roadmap.md), [RFC-002](../rfc/RFC-002-financial-commitments.md)  
**Depends on:** Accounts, Transactions, Dashboard, Goals (`v0.5.0-foundation`)  
**Sprint:** [Sprint 6 — Financial Commitments](../roadmap/sprint-6-financial-commitments.md)  
**Decision:** [Financial Commitments](../decisions/2026-07-25-financial-commitments.md)

---

## Outcome

Users see **Obligaciones** (Financial Commitments). The first type is **Debt**: metadata over a liability account so Net Worth is honest and payments never leave the transaction ledger.

```text
Assets − Liabilities = Net Worth
```

## Non-goals

- Amortization product engines, refinance, bank sync, AI payoff coaching
- Tax obligations as rows (Taxes module later — same UI family)
- Vue work in slice 6.1 (product model only)

## Notes

- Backend: `modules/debts/`  
- UI: `/app/commitments` · label Obligaciones / Financial Commitments  
- **6.1** Accepted (RFC-002) · **6.2** Accepted ([UX flows](../roadmap/sprint-6.2-commitments-ux.md))  
- Implementation: **6.3** API → **6.6** frontend  
