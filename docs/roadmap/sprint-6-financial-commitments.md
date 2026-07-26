# Sprint 6 — Financial Commitments

**Status:** In progress (6.1 Accepted)  
**Epic:** [EPIC-005](../epics/EPIC-005-debts.md)  
**RFC:** [RFC-002 — Financial Commitments / Debt product model](../rfc/RFC-002-financial-commitments.md)  
**Decision:** [Financial Commitments](../decisions/2026-07-25-financial-commitments.md)  
**Baseline tag:** `v0.5.0-foundation`

---

## Product question

> ¿Qué compromete mi dinero futuro?

Backend implements **Debt** first. UI speaks **Obligaciones**.

---

## Slices

| Slice | Focus | Status |
|-------|--------|--------|
| **6.1** | Domain / product model (language + invariants) | **Accepted** — [RFC-002](../rfc/RFC-002-financial-commitments.md) |
| **6.2** | Debt Management (persist + API aligned to RFC) | Next |
| **6.3** | Payment strategies (preferences + recommendations only) | Planned |
| **6.4** | Dashboard integration (liabilities / commitments widgets) | Planned |
| **6.5** | Frontend (Obligaciones UI) | Planned |

Legacy brief [sprint-6-debt-management.md](./sprint-6-debt-management.md) redirects here conceptually; prefer this file.

---

## Exit criteria (Sprint 6 complete)

- [x] Product model frozen in RFC-002  
- [ ] Domain + migration match RFC (creditor, optional enrichment, statuses, 1:1 liability account, no stored balance)  
- [ ] Payments only via Transactions  
- [ ] Strategy preference does not mutate ledger  
- [ ] Dashboard: assets / liabilities / net worth (+ commitment summary if ready)  
- [ ] Nuxt **Obligaciones** UI at Goals quality bar  
- [ ] Demo seed sample obligation  
- [ ] Org isolation + archive history tests  

---

## 6.1 acceptance (done)

See RFC-002 §16. Glossary and Principle 08 published under `docs/product/`.

---

## 6.2 focus (next)

Converge `modules/debts/` to RFC-002:

- Optional interest / minimum payment  
- Creditor + emotional priority  
- Statuses: `paused`, `defaulted`  
- Types: `business_loan`, `family_loan`, `installment_plan`  
- Auto paid_off / revive from account balance  
- Remove any path that treats Debt as a wallet  

---

## Out of scope (whole Sprint 6)

Refinancing, consolidation, amortization engines, credit score, bank import, AI coaching, tax obligations as first-class rows (Taxes module later).

---

## Related principles

[P08 Financial Commitments](../product/02-product-principles.md) · [PRODUCT_LANGUAGE.md](../product/PRODUCT_LANGUAGE.md)
