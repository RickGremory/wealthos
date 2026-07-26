# Sprint 6 — Financial Commitments

**Status:** In progress (6.1–6.3 Accepted)  
**Epic:** [EPIC-005](../epics/EPIC-005-debts.md)  
**RFC:** [RFC-002](../rfc/RFC-002-financial-commitments.md)  
**UX:** [6.2](./sprint-6.2-commitments-ux.md)  
**Integration:** [6.3](./sprint-6.3-commitments-integration.md)  
**Baseline tag:** `v0.5.0-foundation`

---

## Product question

> ¿Qué compromete mi dinero futuro?

Backend: **Debt**. UI: **Financial Commitments / Obligaciones** · `/app/commitments`.

---

## Slices

| Slice | Focus | Status |
|-------|--------|--------|
| **6.1** | Domain / product model | **Accepted** — [RFC-002](../rfc/RFC-002-financial-commitments.md) |
| **6.2** | UX & user flows | **Accepted** — [6.2](./sprint-6.2-commitments-ux.md) |
| **6.3** | Ecosystem integration (+ Financial Timeline reserved) | **Accepted** — [6.3](./sprint-6.3-commitments-integration.md) |
| **6.4** | Debt API / persistence + dashboard projections | **Next** |
| **6.5** | Payment strategy preferences | Planned |
| **6.6** | Dashboard UI (commitments block, attention, NW drill-down) | Planned |
| **6.7** | Frontend Obligaciones (`/app/commitments`) | Planned |

---

## Exit criteria (Sprint 6 complete)

- [x] Product model (RFC-002)  
- [x] UX & flows (6.2)  
- [x] Integration contract (6.3)  
- [ ] Domain + migration + projections (`financial_commitments` on dashboard)  
- [ ] Payments via Transfer/Transactions  
- [ ] Strategy preference does not mutate ledger  
- [ ] Dashboard UI per 6.3  
- [ ] Nuxt Obligaciones per 6.2  
- [ ] Demo seed sample obligation  
- [ ] Org isolation + multi-currency + archive tests  

---

## 6.4 focus (next)

Implement the domain/API that makes 6.1–6.3 real:

- RFC field set (creditor, priority, optional enrichment, statuses, types)  
- Balance only from liability account; auto paid_off / revive  
- Transfer-based payments  
- Dashboard projection `financial_commitments` (by currency, attention derived)  
- Observability events listed in 6.3  
- Calendar event payloads (even if Calendar UI consumes later)  

---

## Out of scope (Sprint 6)

Refinancing, amortization engines, credit score, bank import, AI advice, Timeline UI, bulk actions, tax commitment rows.

---

## Related

[P08](../product/02-product-principles.md) · [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md) · [Financial Timeline](../decisions/2026-07-25-financial-timeline.md)
