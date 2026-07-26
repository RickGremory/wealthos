# Sprint 8.2 — Safe To Spend Calculation Model

**Status:** Accepted  
**Parent:** [Sprint 8](./sprint-8-planning-safe-to-spend.md)  
**Depends on:** [8.1 Domain](./sprint-8.1-planning-domain-model.md) · [RFC-004](../rfc/RFC-004-planning-projection.md)  
**Next:** 8.3 — Module integration (normalized inputs)

> **Frozen calculation contract.** Defines *how* Safe To Spend is computed, what enters, what is excluded, and how the result is explained.  
> No application code in this slice. Implementation follows in 8.5 / SPEC.

---

## Objective

Calculate how much money the user may spend within a horizon without compromising:

- obligations  
- planned / recurring outflows  
- taxes  
- goals (when planned or protected)  
- safety reserve  

The result is an **explainable projection**, never an opaque number.

Functional question:

> ¿Cuánto dinero puedo gastar entre hoy y una fecha determinada sin que mi saldo proyectado caiga por debajo de mis reservas obligatorias?

---

## 1. Result shape (minimum)

```ts
interface SafeToSpendResult {
  currency: string
  horizon: PlanningHorizon
  periodStart: string   // ISO date
  periodEnd: string

  currentAvailableCash: string
  expectedIncome: string
  committedOutflows: string
  reservedFunds: string

  safeToSpend: string | null   // null only when status = insufficient_data | unavailable
  projectedEndingBalance: string | null
  deficit: PlanningDeficit | null

  status: SafeToSpendStatus
  confidence: ProjectionConfidence

  breakdown: PlanningBreakdownItem[]
  alerts: PlanningAlert[]
}

interface PlanningDeficit {
  amount: string
  expectedDate: string
}

interface SafeToSpendWindows {
  today: string
  next7Days: string
  next30Days: string
  next90Days: string
}
```

Dashboard may request a **summary window set**; Planning detail calculates **one horizon per request**. Do not force all four windows inside every detail call.

---

## 2. Conceptual formula

```text
Current available cash
+ Expected income (included by certainty policy)
− Committed outflows (included by certainty policy)
− Reserved funds (goals / tax pending / …)
→ working projection
```

Domain shorthand:

```text
Safe To Spend = f(chronological projected balances, required ending reserve)
```

**Not** a single naive subtraction of totals. Must account for dates, certainty, already-satisfied events, double-counting, excluded accounts, and **one currency only**.

---

## 3. Currency Integrity (P09)

```ts
calculate({ organizationId, currency: "MXN", horizon: "30_days", calculatedAt })
```

- One projection = one currency.  
- Never `MXN + USD`.  
- Multi-currency orgs → independent projections per currency.  
- Response always echoes `"currency": "MXN"`.

---

## 4. Horizons

```ts
type PlanningHorizon =
  | "today"
  | "7_days"
  | "30_days"
  | "90_days"
```

```text
period_start = calendar date of calculatedAt (org timezone)
period_end   = period_start + horizon
```

**30 days ≠ end of month.** Keep concepts separate.  
Deferred (not V1): `end_of_week`, `end_of_month`, `custom`.

---

## 5–6. Eligible cash (not net worth)

Safe To Spend uses **liquid, usable cash** only — never net worth.

**Included by default:** checking, available savings, cash, available wallets.  
**Excluded by default:** investments, retirement, illiquid assets, liabilities, archived, blocked, legally reserved.

```ts
interface PlanningEligibleAccount {
  accountId: string
  availableBalance: string
  currency: string
  included: boolean
  exclusionReason: string | null
}
```

Input concept is **Available Cash**, not raw `current_balance`.

V1 default when per-account reserves do not exist:

```text
available_balance = current_balance
```

Interface must still allow `available ≠ accounting` later. Org settings may refine inclusion later.

---

## 7–9. Expected cash flows & certainty

```ts
type CashFlowCertainty = "confirmed" | "expected" | "estimated"
type CashFlowStatus = "pending" | "satisfied" | "cancelled" | "excluded"

interface ExpectedCashFlow {
  id: string
  sourceType: PlanningSourceType
  sourceId: string | null
  direction: "inflow" | "outflow"
  amount: string
  currency: string
  expectedDate: string
  certainty: CashFlowCertainty
  status: CashFlowStatus
  occurrenceKey: string   // for dedupe — see §30
}
```

### Inclusion policy (V1)

| Certainty | Inflows | Outflows |
|-----------|---------|----------|
| `confirmed` | include 100% | include |
| `expected` | include if `includeExpectedIncome` (default **true**) | include |
| `estimated` | **exclude** from Safe To Spend | may include if `includeEstimatedExpenses` (default **true**, conservative) |

**Principle:** Uncertain income must not inflate safe spend. Probable outflows should reduce it when risk is reasonable.

Estimated inflows may appear in a secondary “optimistic” view later — **not** in Safe To Spend V1.

---

## 10–11. Committed outflows & obligations

```ts
type PlanningOutflowCategory =
  | "commitment"
  | "recurring_expense"
  | "tax"
  | "goal_allocation"
  | "planned_expense"
  | "safety_reserve"
```

### Commitments

From Commitments module: `required_payment` / next action amount, `next_due_date`, `currency`, `status`.

Include when `next_due_date <= period_end` **or** already overdue.

**Anti double-count:** if a payment transaction already covers the occurrence in-period, consume only the **remaining** pending amount (reconcile expected commitment payment vs posted transfers).

---

## 12. Recurring expenses

Generate **dated occurrences** inside the horizon (calendar-aware).

Do **not** use `amount × N` without dates — occurrence count depends on the calendar.

Example: internet 800 on day 15 over 90 days → three dated events.

---

## 13. Goals — funding modes

```ts
type GoalFundingMode = "informational" | "planned" | "protected"
```

| Mode | Effect on Safe To Spend |
|------|-------------------------|
| `informational` | Progress only — **no** reduction |
| `planned` | Expected contribution on date — reduces when due in horizon |
| `protected` | Linked balances treated as **reserved** (not available cash) |

Goals never auto-drain liquidity without an explicit user/org mode.

---

## 14. Taxes

Distinguish: accrued · reserved · due · paid.

Discount only the **still-unprotected** amount:

```text
estimated 10_000 − already reserved 6_000 = pending 4_000  → subtract 4_000
```

Never subtract full estimated tax *and* the reserved cash again.

---

## 15. Safety reserve

Minimum balance that must remain at **every** point after simulating spend (see §17–19), not only at period end in isolation.

```ts
type SafetyReserveStrategy =
  | "none"
  | "fixed_amount"
  | "percentage_of_cash"
  | "days_of_expenses"
  | "linked_goal"
```

**V1 implement first:** `none` · `fixed_amount` · `linked_goal`.  
Defer full support for `% of cash` and `days_of_expenses` (may stub → treat as `none` + alert).

Default settings: `safety_reserve_strategy = none` with alert `safety_reserve_not_configured` (confidence capped at medium). Calculation still runs.

---

## 16. Calculation sequence

1. Resolve org, currency, horizon, `calculatedAt`  
2. Eligible accounts → current available cash  
3. Generate future events in `[period_start, period_end]`  
4. Remove / reduce events already satisfied by real transactions  
5. Classify by certainty  
6. Apply inclusion policies  
7. Project balance **chronologically**  
8. Compute required safety reserve  
9. Find **minimum** projected balance over the period (including t0)  
10. Derive Safe To Spend + breakdown + alerts + confidence  

---

## 17–19. Chronological minimum (critical)

**Do not** use only ending balance.

Example: start 10_000 → rent −8_000 day 5 → payroll +15_000 day 15. Ending 17_000 does **not** mean today can spend 17_000.

```text
Safe To Spend = max(0, minimum_projected_balance − required_safety_reserve)
```

After simulating spending that amount **today**, no point in the horizon may fall below the required reserve.

If reserve = 2_000 and trough = 2_000 → Safe To Spend = 0 (survive rent before payroll).

---

## 21–22. Non-negative spendable + status

```text
safe_to_spend = max(0, raw_result)
```

Always expose **deficit** when the projection breaches reserve / goes negative:

```ts
type SafeToSpendStatus =
  | "healthy"
  | "limited"
  | "zero"
  | "deficit"
  | "insufficient_data"
  | "unavailable"
```

Suggested rules (thresholds via policy, not hard-coded UI colors):

| Condition | Status |
|-----------|--------|
| Spendable > comfortable margin vs reserve | `healthy` |
| Spendable > 0 but thin margin | `limited` |
| Spendable = 0, no breach beyond reserve path | `zero` |
| Trough below reserve / negative path | `deficit` |
| Cannot compute meaningfully | `insufficient_data` |
| Module / currency blocked | `unavailable` |

**Never** return `safe_to_spend: "0"` for insufficient data — use `null` + alerts (zero means “computed, no room”).

---

## 23. Confidence

```ts
type ProjectionConfidence = "high" | "medium" | "low"
```

| Level | When |
|-------|------|
| `high` | Major outflows confirmed; included income confirmed; critical settings present |
| `medium` | Expected flows present; some approximate dates; or reserve not configured |
| `low` | Missing payments; many estimated events; weak recurring coverage |

Confidence **explains reliability**; it does not silently rescale the amount.

---

## 24. Breakdown

```ts
interface PlanningBreakdownItem {
  id: string
  category: PlanningOutflowCategory | "current_cash" | "expected_income"
  label: string
  amount: string
  currency: string
  date: string | null
  direction: "add" | "subtract"
  sourceType: PlanningSourceType
  sourceId: string | null
  certainty: CashFlowCertainty
  included: boolean
  exclusionReason: string | null
}
```

Example narrative:

```text
Saldo disponible                    +50_000
Nómina esperada 15 ago              +30_000
Pago tarjeta HSBC                    −6_300
Internet                               −800
Reserva de impuestos                 −4_000
Fondo mínimo                        −10_000
→ Disponible para gastar             21_700
```

Copy tone: *Según la información registrada…* — never absolute “sin ningún riesgo”.

---

## 25. Domain policies

| Policy | Role |
|--------|------|
| `EligibleAccountsPolicy` | Liquid accounts in/out |
| `IncomeInclusionPolicy` | Certainty gates for inflows |
| `CommitmentOutflowPolicy` | Due / overdue obligations + payment reconciliation |
| `RecurringOutflowPolicy` | Occurrence generation |
| `GoalReservationPolicy` | informational / planned / protected |
| `TaxReservationPolicy` | Pending tax protection only |
| `SafetyReservePolicy` | Required reserve amount |
| `ProjectionConfidencePolicy` | high / medium / low |
| `SafeToSpendPolicy` | Chronological trough → spendable + status |

Policies receive context and return contributions / decisions. **They never mutate external modules.**

---

## 26–27. Context & determinism

```ts
interface PlanningContext {
  organizationId: string
  currency: string
  calculatedAt: string
  periodStart: string
  periodEnd: string
  settings: PlanningSettings
  accounts: PlanningAccountSnapshot[]
  expectedCashFlows: ExpectedCashFlow[]
  commitments: PlanningCommitment[]
  goals: PlanningGoal[]
  taxes: PlanningTaxReservation[]
}
```

```text
same PlanningContext → same SafeToSpendResult
```

Forbidden inside the pure engine: wall-clock `now()`, external HTTP, repository calls, randomness.  
`calculatedAt` is an **explicit input**.

---

## 28. Same-day ordering (conservative)

If inflow and outflow share a date without reliable time:

**Process outflows before inflows.**

Suggested order within a day:

1. Overdue  
2. Confirmed outflows  
3. Expected outflows  
4. Confirmed inflows  
5. Expected inflows  

Respect explicit times when trustworthy.

---

## 29. Missing exact dates

| Case | Rule |
|------|------|
| Monthly due day | Materialize calendar date in horizon |
| Expense “this month” without day | Conservative date (early in remaining window) |
| Income without date | **Exclude** from Safe To Spend + alert |
| Outflow without date | Include early **or** warn by type — prefer prudence |

Uncertainty on income → lower confidence. Uncertainty on outflow → prudence.

---

## 30. Deduplication

```ts
interface PlanningSourceReference {
  sourceType: string
  sourceId: string
  occurrenceKey: string  // e.g. commitment:{id}:due:2026-08-28
}
```

Dedupe risks: commitment also as recurring; goal + scheduled transfer; tax reserved in cash **and** as outflow; future payment already posted.

One `occurrenceKey` → at most one effect on the projection.

---

## 31–32. PlanningSettings (persistable)

```ts
interface PlanningSettings {
  organizationId: string
  defaultHorizon: PlanningHorizon
  includedCertainties: CashFlowCertainty[]
  safetyReserveStrategy: SafetyReserveStrategy
  safetyReserveAmount: string | null
  linkedEmergencyGoalId: string | null
  includeExpectedIncome: boolean
  includeEstimatedExpenses: boolean
  createdAt: string
  updatedAt: string
}
```

**Recommended defaults:**

```text
default_horizon = 30_days
include_expected_income = true
include_estimated_expenses = true
safety_reserve_strategy = none
```

Onboarding later invites configuring a reserve. Without reserve: compute + alert; confidence ≤ medium.

---

## 33–34. Insufficient data & alerts

Examples of `insufficient_data`: no eligible accounts; unknown currency; all accounts excluded; critical balance errors.

```json
{
  "status": "insufficient_data",
  "safe_to_spend": null,
  "alerts": [{ "code": "no_eligible_accounts", "severity": "critical" }]
}
```

Initial alert codes:

`projected_deficit` · `safety_reserve_not_configured` · `low_projection_confidence` · `missing_expected_income_date` · `missing_commitment_payment` · `duplicate_cash_flow_excluded` · `stale_account_balance` · `goal_allocation_at_risk` · `tax_reservation_incomplete` · `no_eligible_accounts`

```ts
interface PlanningAlert {
  code: string
  severity: "info" | "warning" | "critical"
  messageKey: string
  relatedResourceType: string | null
  relatedResourceId: string | null
  date: string | null
  amount: string | null
  currency: string | null
}
```

---

## 35. Explicit non-goals (engine)

Must **not**: recommend investments; evaluate products; AI-infer income; statistical spend prediction; FX convert; move money; mutate goals; create payments; promise absolute safety.

---

## 36. Worked example

```text
Cash now                         50_000 MXN
5 ago  Rent                     −12_000 → 38_000
10 ago Card                      −6_300 → 31_700
15 ago Payroll                  +30_000 → 61_700
20 ago Tax reserve               −4_000 → 57_700
Safety reserve                   10_000

minimum_projected_balance = 31_700
Safe To Spend = max(0, 31_700 − 10_000) = 21_700 MXN
```

---

## Acceptance criteria (8.2)

- [x] Per currency + horizon  
- [x] Liquid eligible accounts only  
- [x] Chronological projection  
- [x] Uses period **minimum** balance, not only ending  
- [x] Same-day: outflows before undated inflows  
- [x] Uncertain income does not inflate result  
- [x] Probable outflows treated conservatively  
- [x] Dedup strategy for commitments / recurring / goals / taxes  
- [x] Spendable never negative; deficits reported  
- [x] Breakdown + alerts + confidence  
- [x] Deterministic given `PlanningContext`  
- [x] Result computed dynamically — never persisted  

---

## Next

**8.3** — How Accounts, Transactions, Commitments, Goals, Taxes (and Recurring stubs) produce the normalized inputs this engine consumes.
