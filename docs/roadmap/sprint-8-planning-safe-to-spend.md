# Sprint 8 — Planning & Safe To Spend

**Status:** Design complete (8.1–8.4 Accepted) — **implementation via 8.5 / SPEC**  
**Epic:** [EPIC-007](../epics/EPIC-007-planning-safe-to-spend.md)  
**RFC:** [RFC-004](../rfc/RFC-004-planning-projection.md)  
**Decisions:** [Projection](../decisions/2026-07-25-safe-to-spend-projection.md) · [Chronological trough](../decisions/2026-07-25-safe-to-spend-chronological.md) · [Adapters / occurrence_key](../decisions/2026-07-25-planning-adapters-occurrence-key.md) · [UX three numbers](../decisions/2026-07-25-planning-ux-three-numbers.md)

---

## Product question

> ¿Cuánto dinero puedo usar hoy sin comprometer mi futuro financiero?

Safe To Spend is a **consequence of Financial Projection**, not a stored balance.

---

## Design pillars

| Slice | Focus | Status |
|-------|--------|--------|
| **8.1** | Domain / product model | **Accepted** — [8.1](./sprint-8.1-planning-domain-model.md) · [RFC-004](../rfc/RFC-004-planning-projection.md) |
| **8.2** | Safe To Spend algorithm (policies) | **Accepted** — [8.2](./sprint-8.2-safe-to-spend-algorithm.md) |
| **8.3** | Integration with Goals, Commitments, Taxes | **Accepted** — [8.3](./sprint-8.3-planning-integration.md) |
| **8.4** | UX + “¿Qué pasa si…?” scenarios | **Accepted** — [8.4](./sprint-8.4-planning-ux-scenarios.md) |
| **8.5** | Technical SPEC + implementation | Planned |

---

## Why this sprint after Timeline

Timeline is the narrative glue. Safe To Spend is the reason to open the app daily. Core facts exist; Planning now orchestrates them into a decision surface.

## Out of scope (Sprint 8)

AI Financial Assistant · CSV/Open Banking · year horizons · Planning writes to the ledger

## Related

[Principle 10](../product/02-product-principles.md) · [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md)
