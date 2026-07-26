# Sprint 8.1 — Planning Domain Model

**Status:** Accepted  
**Parent:** [Sprint 8](./sprint-8-planning-safe-to-spend.md)  
**Contract:** [RFC-004](../rfc/RFC-004-planning-projection.md)  
**Decision:** [Safe To Spend as Financial Projection](../decisions/2026-07-25-safe-to-spend-projection.md)

---

## Objective

Model **future money** — money not yet spent that already has a destiny — without writing application code.

Until now WealthOS modeled existing money, past movements, and current net worth. Planning introduces **hypothesis**: projections over facts and forecasts.

---

## Product Principle

> Not all available money is spendable money.

Codified as **[Principle 10](../product/02-product-principles.md)** (P09 remains Currency Integrity).

---

## Distinction

| Surface | Question |
|---------|----------|
| Account / balance | ¿Cuánto dinero tengo? |
| Planning / Safe To Spend | ¿Cuánto puedo utilizar sin afectar mi futuro? |

Never conflate them in UI or API.

---

## Start from Financial Projection

Do **not** start from a lone Safe To Spend number.

```text
Today
  → Current Cash (fact)
  → Future Events (facts + forecasts)
  → Financial Projection
  → Safe To Spend (consequence)
```

Safe To Spend never reads Accounts directly as its only input. It reads a **projection**.

---

## Aggregate (conceptual)

`PlanningProjection` — photograph of the future. **Not persisted.** Always calculated.

Includes current cash, expected income, planned expenses, commitments, goal allocations, tax reservations, safety reserve, safe-to-spend, committed/reserved totals, alerts, recommendations, explanation chain, fact/forecast mix, `generated_at`.

Horizons share one interface: Today / Week (7d) / Month (30d) / Quarter (90d).

---

## Money states

1. **Disponible** — may still be used  
2. **Comprometido** — known destination (obligations, fixed outflows)  
3. **Reservado** — should not touch (tax, goals, safety)  
4. **Gastado** — already happened  

Dashboard language shifts from “tengo 50k” to available / committed / reserved.

---

## Facts vs Forecasts

Planning is the first module that primarily works on **hypotheses**.

| | |
|--|--|
| **Facts** | Confirmed ledger and commitment existence |
| **Forecasts** | Expected income, future payments, planned savings |

Every projection must expose the mix so users (and later AI) know confidence.

---

## Sources (orchestrate, never duplicate)

```text
Accounts → Transactions → Recurring* → Commitments → Goals → Taxes → Timeline*
                                    ↓
                               Planning
```

\* May be partial/stub in early slices.

---

## Policies (not one mega-method)

```text
IncomePolicy → CommitmentPolicy → GoalsPolicy → TaxPolicy → ReservePolicy → ProjectionPolicy
```

---

## Persistence

| Persist | Do not persist |
|---------|----------------|
| `PlanningSettings` (reserve strategy, horizon preference, emergency goal link, …) | `safe_to_spend`, full projections |

---

## Invariants

1–5: Planning never mutates money, transactions, goals, obligations, or balances.  
6: Always explain the result.  
7: Currency Integrity (P09) — per-currency projections only.

---

## Explicit non-belonging

Not in 8.1: UI, Dashboard polish, charts, Calendar, Timeline event emitters, algorithm numbers.

---

## Acceptance checklist

- [x] Projection domain model exists in RFC-004  
- [x] Safe To Spend = projection consequence  
- [x] Four money states named  
- [x] Consume-other-modules / no duplicate ledger  
- [x] Ephemeral projections  
- [x] Horizons today / 7 / 30 / 90  
- [x] Policy-oriented calculation shape  
- [x] Facts vs Forecasts first-class  
- [x] Principle 10 + language + decision logged  

---

## Next

**8.2** — Policy algorithm and numeric rules for Safe To Spend.
