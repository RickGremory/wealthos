# RFC-004

# Planning Projection — Safe To Spend Domain Model

**Author:** Ricardo Balam  
**Status:** Accepted (Sprint 8.1 — Domain / Product Model)  
**Created:** 2026-07-25  
**Sprint slice:** 8.1  
**Baseline:** post–SPEC-003 (Financial Timeline)

> **Frozen as product/domain contract for Planning’s projection spine.**  
> Do not invent a persisted `safe_to_spend` column, a second ledger, or UI that treats balance as spendable cash.  
> Execution continues via [EPIC-007](../epics/EPIC-007-planning-safe-to-spend.md) and later Sprint 8 SPECs.  
> See [PRODUCT_LANGUAGE.md](../product/PRODUCT_LANGUAGE.md) and [Principle 10](../product/02-product-principles.md).

---

## Summary

WealthOS models **money that has not been spent yet but already has a destiny**.

```text
Facts + Forecasts
        │
        ▼
Financial Projection  (PlanningProjection — computed, not persisted)
        │
        ├── Money states: Disponible | Comprometido | Reservado | Gastado
        ├── Horizons: today | 7d | 30d | 90d
        └── Consequence: Safe To Spend (+ explanation chain)
```

**Safe To Spend** is never a primary stored fact. It is derived from the projection after policies for income, commitments, goals, taxes, and reserve.

Existing `modules/planning/` capabilities (budgets, cash plans) remain **tools** that can feed forecasts. They are not a second source of truth for balances.

---

## Motivation

Accounts answer *¿Cuánto dinero tengo?*  
Planning must answer *¿Cuánto puedo utilizar sin afectar mi futuro financiero?*

Those questions must never be confused (Principle 10).

With Accounts, Transactions, Commitments, Goals, Taxes, and Timeline in place, the ingredients exist. Recurring will enrich forecasts later without changing this model.

---

## Goals

- One projection aggregate shape (`PlanningProjection`) for all horizons  
- Explicit **Facts vs Forecasts** on every result (confidence for humans and future AI)  
- Four money states: available / committed / reserved / spent  
- Policy chain (composable rules), not a monolithic calculator  
- Explainable output (chain of deductions), never a bare number  
- Persist **settings only**; recompute projections on demand  

## Non-goals (Sprint 8.1)

- Algorithm numeric detail (→ 8.2)  
- Full Goals/Commitments/Taxes wiring code (→ 8.3)  
- UX / “what if” scenarios UI (→ 8.4)  
- Implementation SPEC / Vue (→ 8.5)  
- AI recommendations, bank import, year-long projections  
- Planning mutating money, goals, or commitments  

---

## Principles applied

| Principle | How it shows up |
|-----------|-----------------|
| P01 Financial Truth | Every Safe To Spend number has an explanation chain |
| P02 One Source of Truth | Planning never duplicates balances |
| P04 Context | Horizons + currency slices; never global FX sums (P09) |
| P05 Planning Before Automation | Rules/recommendations before AI |
| P08 Commitments | Commitments reduce spendable cash as **committed** |
| P10 Spendable ≠ Available | Core of this RFC |

---

## Core concepts

### Financial Projection / `PlanningProjection`

A **photograph of the future** for one organization, one currency, one horizon.

Not a table row. Always calculated. Generated at `generated_at`.

Conceptual contents:

| Field | Meaning |
|-------|---------|
| `current_cash` | Fact — liquid balances from Accounts |
| `expected_income` | Forecast — upcoming income |
| `planned_expenses` | Forecast — planned / recurring outflows |
| `commitments` | Mix — scheduled obligation payments in horizon |
| `goal_allocations` | Reserved — planned savings toward goals |
| `tax_reservations` | Reserved — tax set-asides |
| `safety_reserve` | Reserved — emergency / policy buffer |
| `safe_to_spend` | Consequence — after policies |
| `committed_money` | Sum of committed claims in horizon |
| `reserved_money` | Sum of reserves (goals, tax, safety) |
| `projected_balance` | End-of-horizon sketch |
| `fact_share` / `forecast_share` | Explicit mix for confidence |
| `alerts` | Soft warnings (not errors) |
| `recommendations` | Rule-based guidance (not AI yet) |
| `explanation` | Ordered deduction steps (human copy) |

### Safe To Spend

Product surface name for the projection consequence.

Answers: *¿Cuánto puedo gastar con tranquilidad en este horizonte?*

Must always ship with:

1. **Disponible** (safe to spend)  
2. **Comprometido** (already claimed)  
3. Explanation of *why* (balance → deductions → result)

### Money states

| State (ES) | EN | Meaning |
|------------|-----|---------|
| Disponible | Available / spendable | May be used without breaking the plan |
| Comprometido | Committed | Known future destination (obligations, fixed outflows) |
| Reservado | Reserved | Should not be touched (tax, goals, safety) |
| Gastado | Spent | Already occurred (facts from ledger) |

### Facts vs Forecasts

| Kind | Examples |
|------|----------|
| **Fact** | Posted transactions, current account balances, existing commitments metadata |
| **Forecast** | Expected income, planned expenses, scheduled commitment payments not yet paid, planned goal contributions |

Every `PlanningResult` must indicate what portion of the calculation rests on facts vs forecasts. That enables trust UX and future AI confidence language.

### Horizons

Only:

- **Today** — `TodayProjection`  
- **7 days** — `WeekProjection`  
- **30 days** — `MonthProjection`  
- **90 days** — `QuarterProjection`  

Same interface; different window. No 1-year MVP horizon.

### Policies (calculation spine)

Independent policies mutate / annotate a working projection:

```text
IncomePolicy
  → CommitmentPolicy
  → GoalsPolicy
  → TaxPolicy
  → ReservePolicy
  → ProjectionPolicy (finalize Safe To Spend + explanation)
```

Adding a rule later = new policy (or policy version), not rewriting a mega-function.

### Alerts vs recommendations

- **Alerts** — risk signals (*flujo negativo en 12 días*, *colchón bajo el mínimo*).  
- **Recommendations** — rule-based next orientations (*paga primero X*, *pospone compra*).  
Neither mutates the ledger. AI comes later and **consumes** this structure.

### PlanningSettings (persistable)

Organization-scoped preferences only, e.g.:

- Reserve strategy / safety buffer parameters  
- Default projection horizon  
- Linked emergency-fund goal (optional)  
- Default currency for projection display (still P09-sliced)

**Never persist** computed `safe_to_spend`.

---

## Module boundaries

```text
Accounts · Transactions · Commitments · Goals · Taxes · Recurring* · Timeline*
        │
        ▼
modules/planning/   ← orchestrates projection
        │
        ├── PlanningProjection (computed)
        ├── PlanningSettings (persisted)
        └── (existing) Budget / CashPlan tools as forecast inputs
```

\* Recurring / richer Timeline hooks may be stubs until those modules mature.

**Direction:** Planning knows other modules. Other modules do **not** depend on Planning.

### Invariants

1. Planning never modifies money.  
2. Planning never creates transactions.  
3. Planning never changes goals.  
4. Planning never pays obligations.  
5. Planning never mutates account balances.  
6. Planning always explains the result (no bare number as sole API/UI output).  
7. Multi-currency: project **per currency**; never sum cross-currency (P09).

---

## Relationship to existing planning code

Budgets and cash plans already live under `modules/planning/`. Sprint 8 does **not** delete them.

They become **forecast instruments** and settings surfaces that feed `PlanningProjection`. Safe To Spend / Financial Projection is the **product spine**; budgets/cash plans are supporting tools.

---

## Acceptance criteria (8.1)

- [x] Domain model for financial projections documented  
- [x] Safe To Spend defined as projection consequence, not independent datum  
- [x] Money classified: available / committed / reserved / spent  
- [x] Planning consumes other modules without duplicating ledgers  
- [x] Projections are ephemeral (not persisted)  
- [x] Horizons prepared: today / 7d / 30d / 90d  
- [x] Calculation organized as independent policies  
- [x] Facts vs Forecasts made first-class  
- [x] Decision + Principle 10 + PRODUCT_LANGUAGE updated  

---

## Success criteria (Sprint 8 overall — foreshadow)

User opens Dashboard and sees spendable + committed with an explanation chain fed by real Commitments, Goals, and Taxes — not “aún no calculado”.

---

## Open points deferred to 8.2+

- Exact policy math and ordering edge cases  
- How cash-plan occurrences map into forecast lines  
- What-if scenario engine shape  
- Timeline events when Safe To Spend changes materially  
