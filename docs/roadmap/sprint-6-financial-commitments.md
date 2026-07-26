# Sprint 6 — Financial Commitments

**Status:** Design complete (6.1–6.5 Accepted) — **implementation via [SPEC-002](../../specs/backend/debts/SPEC-002-financial-commitments.md)**  
**Epic:** [EPIC-005](../epics/EPIC-005-debts.md)  
**Baseline tag:** `v0.5.0-foundation`

---

## Product question

> ¿Qué compromete mi dinero futuro?

Backend: `modules/debts/`. API/UI: **commitments / Obligaciones** · `/app/commitments`.

---

## Design pillars (frozen)

| Slice | Focus | Status |
|-------|--------|--------|
| **6.1** | Domain / product model | **Accepted** — [RFC-002](../rfc/RFC-002-financial-commitments.md) |
| **6.2** | UX & user flows | **Accepted** — [6.2](./sprint-6.2-commitments-ux.md) |
| **6.3** | Ecosystem integration (+ Timeline reserved) | **Accepted** — [6.3](./sprint-6.3-commitments-integration.md) |
| **6.4** | Payment strategies & recommendations | **Accepted** — [6.4](./sprint-6.4-payment-strategies.md) |
| **6.5** | Frontend & implementation specification | **Accepted** — [6.5](./sprint-6.5-implementation-spec.md) · **[SPEC-002](../../specs/backend/debts/SPEC-002-financial-commitments.md)** |

Day-to-day coding follows **SPEC-002** (phases, checkboxes, commit plan). Do not reopen 6.1–6.4 for implementation details.

---

## Exit criteria (Sprint 6 complete)

- [x] Design pillars 6.1–6.5 Accepted  
- [ ] SPEC-002 Completed (golden path live)  
- [ ] Demo seed + E2E green  
- [ ] README / epic marked Done for Commitments MVP  

---

## Golden path (DoD)

```text
Create card → liability link → balance + due + next action
→ strategy → Dashboard + Calendar → transfer payment
→ balances / strategy / net worth refresh → timeline-ready event
```

---

## Out of scope

Bank import, auto-pay, full amortization, refinance, AI advice, Timeline UI, FX sums, multi-MSI under one card.

---

## Related

[P08](../product/02-product-principles.md) · [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md)
