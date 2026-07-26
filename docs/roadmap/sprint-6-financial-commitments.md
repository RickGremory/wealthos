# Sprint 6 — Financial Commitments

**Status:** In progress (6.1–6.4 Accepted)  
**Epic:** [EPIC-005](../epics/EPIC-005-debts.md)  
**RFC:** [RFC-002](../rfc/RFC-002-financial-commitments.md)  
**UX:** [6.2](./sprint-6.2-commitments-ux.md)  
**Integration:** [6.3](./sprint-6.3-commitments-integration.md)  
**Strategies:** [6.4](./sprint-6.4-payment-strategies.md)  
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
| **6.3** | Ecosystem integration (+ Financial Timeline) | **Accepted** — [6.3](./sprint-6.3-commitments-integration.md) |
| **6.4** | Payment strategies & recommendations | **Accepted** — [6.4](./sprint-6.4-payment-strategies.md) |
| **6.5** | Frontend & implementation specification (+ domain/API delivery) | **Next** |

Design pillars **6.1–6.4** are frozen. **6.5** is the executable build plan (routes, DTOs, composables, tests, commits) and the implementation pass that lands API, projections, dashboard UI, and `/app/commitments`.

---

## Exit criteria (Sprint 6 complete)

- [x] Product model (RFC-002 + settled/paid_off refinement)  
- [x] UX & flows (6.2)  
- [x] Integration contract (6.3)  
- [x] Payment strategies (6.4)  
- [ ] Domain/API + org `debt_strategy` + strategy projection endpoint  
- [ ] Dashboard `financial_commitments` + Needs Attention  
- [ ] Nuxt Obligaciones per 6.2–6.4  
- [ ] Payments via Transfer only  
- [ ] Demo seed + tests (org, multi-currency, archive, strategy honesty)  

---

## 6.5 focus (next)

Executable Frontend & Implementation Specification, then build end-to-end:

- Routes `/app/commitments`  
- Repositories, DTOs, ViewModels, composables, components  
- Cache invalidation, permissions, errors  
- Unit / component / E2E tests  
- Suggested commits  
- Backend alignment still owed from RFC + 6.3–6.4 (fields, projections, `DebtStrategyService`)

---

## Out of scope (Sprint 6)

Refinancing, full amortization simulators, exact savings promises, credit score, bank import, AI advice, Timeline UI, bulk actions, tax commitment rows, inventing extra payments without a debt budget.

---

## Related

[P08](../product/02-product-principles.md) · [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md) · [Payment strategies decision](../decisions/2026-07-25-payment-strategies.md)
