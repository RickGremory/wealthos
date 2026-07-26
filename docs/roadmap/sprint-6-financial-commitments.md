# Sprint 6 — Financial Commitments

**Status:** In progress (6.1–6.2 Accepted)  
**Epic:** [EPIC-005](../epics/EPIC-005-debts.md)  
**RFC:** [RFC-002 — Debt product model](../rfc/RFC-002-financial-commitments.md)  
**UX:** [Sprint 6.2 — UX & User Flows](./sprint-6.2-commitments-ux.md)  
**Baseline tag:** `v0.5.0-foundation`

---

## Product question

> ¿Qué compromete mi dinero futuro?

Backend implements **Debt** first. UI speaks **Financial Commitments / Obligaciones** at `/app/commitments`.

---

## Slices

| Slice | Focus | Status |
|-------|--------|--------|
| **6.1** | Domain / product model | **Accepted** — [RFC-002](../rfc/RFC-002-financial-commitments.md) |
| **6.2** | UX & user flows (cards, next action, create flow) | **Accepted** — [6.2 UX](./sprint-6.2-commitments-ux.md) |
| **6.3** | Debt API / persistence aligned to RFC + UX needs | **Next** |
| **6.4** | Payment strategy preferences | Planned |
| **6.5** | Dashboard widget (3 signals) | Planned |
| **6.6** | Frontend Obligaciones (`/app/commitments`) | Planned |

---

## Exit criteria (Sprint 6 complete)

- [x] Product model frozen in RFC-002  
- [x] UX & flows frozen in 6.2 (including Next Action pattern)  
- [ ] Domain + migration match RFC (creditor, optional enrichment, statuses, 1:1 liability account, no stored balance)  
- [ ] Payments only via Transactions / Transfer  
- [ ] Strategy preference does not mutate ledger  
- [ ] Dashboard: three commitment signals (+ assets/liabilities/net worth as ready)  
- [ ] Nuxt **Obligaciones** UI per 6.2  
- [ ] Demo seed sample obligation  
- [ ] Org isolation + archive history tests  

---

## 6.3 focus (next)

Converge `modules/debts/` to RFC-002 **and** fields required by UX:

- Optional interest / minimum payment / credit limit / due day  
- Creditor + emotional priority  
- Statuses: `paused`, `defaulted` (+ UX-derived overdue)  
- Types including MSI / family / business  
- Auto paid_off / revive from account balance  
- Transfer-based payment path with preselected liability  
- Summary endpoints for the four index cards + three dashboard signals  

---

## Out of scope (whole Sprint 6)

Refinancing, consolidation, amortization engines, credit score, bank import, AI coaching, bulk actions, tax obligations as first-class rows.

---

## Related

[P08](../product/02-product-principles.md) · [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md) · [Next Action decision](../decisions/2026-07-25-commitments-ux-next-action.md)
