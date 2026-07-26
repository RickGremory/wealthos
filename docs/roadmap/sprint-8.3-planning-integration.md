# Sprint 8.3 — Planning Integration

**Status:** Accepted  
**Parent:** [Sprint 8](./sprint-8-planning-safe-to-spend.md)  
**Depends on:** [8.1](./sprint-8.1-planning-domain-model.md) · [8.2](./sprint-8.2-safe-to-spend-algorithm.md) · [RFC-004](../rfc/RFC-004-planning-projection.md)  
**Next:** 8.4 — UX + “¿Qué pasa si…?”

> **Frozen integration contract.** Planning consumes **normalized financial contracts**, never other modules’ ORM entities.  
> No application code in this slice. Adapters + ports land in 8.5 / SPEC.

---

## Objective

Connect Planning to existing modules **without duplicating their models** and **without** the projection engine querying their tables.

Transform heterogeneous data from Accounts, Transactions, Commitments, Goals, Taxes, and Recurring into a small set of inputs the engine already understands ([8.2](./sprint-8.2-safe-to-spend-algorithm.md)).

### Architectural rule

```text
Planning knows financial contracts — not internal models of other modules.
```

Forbidden in the engine / domain policies:

```python
from wealthos.modules.debts.infrastructure.models import DebtModel
from wealthos.modules.goals.infrastructure.models import GoalModel
```

The engine receives Planning DTOs only.

---

## 1. General flow

```text
Accounts ───────────┐
Transactions ───────┤
Commitments ────────┤
Goals ──────────────┼──> Planning Adapters
Taxes ──────────────┤          ↓
Recurring ──────────┘    PlanningContext
Manual Planned CF ───────      ↓
                        Projection Engine (8.2)
                               ↓
                       SafeToSpendResult
```

---

## 2. Four normalized concepts

| Concept | Role |
|---------|------|
| **`PlanningAccountSnapshot`** | Liquidity today |
| **`PlanningCashFlow`** | Future inflows / outflows in the horizon |
| **`PlanningReservation`** | Money that exists but must not count as spendable |
| **`PlanningSettlement`** | Posted transactions that satisfy projected occurrences (anti double-count) |

Plus **`PlanningSourceReference`** (`occurrence_key`) as the cross-cutting identity.

---

## 3. Core contracts

### PlanningAccountSnapshot

```python
@dataclass(frozen=True)
class PlanningAccountSnapshot:
    account_id: UUID
    organization_id: UUID
    name: str
    account_type: str
    currency: str
    ledger_balance: Decimal
    available_balance: Decimal
    is_liquid: bool
    is_included: bool
    exclusion_reason: str | None
    balance_as_of: datetime
```

Rules: one currency; liabilities never contribute cash; archived → excluded or omitted; `balance_as_of` enables staleness alerts.  
V1: `available_balance = ledger_balance` when account-level holds do not exist.

Liquidity ≠ fully spendable: Goals may reserve liquid cash via `PlanningReservation`.

### PlanningCashFlow

```python
CashFlowDirection = Literal["inflow", "outflow"]
CashFlowCertainty = Literal["confirmed", "expected", "estimated"]
CashFlowStatus = Literal["pending", "partially_settled", "settled", "cancelled"]

@dataclass(frozen=True)
class PlanningCashFlow:
    id: str
    organization_id: UUID
    direction: CashFlowDirection
    amount: Decimal                 # original
    outstanding_amount: Decimal     # still affects projection
    currency: str
    expected_at: datetime
    certainty: CashFlowCertainty
    status: CashFlowStatus
    category: str
    label: str
    source: PlanningSourceReference
    metadata: dict[str, object]
```

Engine consumes **`outstanding_amount`** (e.g. required 5_000 − paid 2_000 → outstanding 3_000).

### PlanningReservation

```python
ReservationType = Literal["tax", "goal", "safety", "legal", "manual"]

@dataclass(frozen=True)
class PlanningReservation:
    id: str
    organization_id: UUID
    reservation_type: ReservationType
    label: str
    required_amount: Decimal
    already_protected_amount: Decimal
    outstanding_amount: Decimal
    currency: str
    effective_at: datetime | None
    source: PlanningSourceReference
    metadata: dict[str, object]
```

A reservation is **not always a future outflow** (e.g. existing emergency fund reduces usable cash without a dated expense).

### PlanningSourceReference

```python
@dataclass(frozen=True)
class PlanningSourceReference:
    source_type: str
    source_id: str
    occurrence_key: str          # stable identity
    resource_version: int | None = None
```

Examples:

```text
commitment:{id}:due:2026-08-15
recurring:{id}:occurrence:2026-08-20
goal:{id}:contribution:2026-08
tax:{id}:period:2026-07:payment
planned:{id}
```

Same obligation processed twice → same key.

### PlanningSettlement

```python
@dataclass(frozen=True)
class PlanningSettlement:
    transaction_id: UUID
    organization_id: UUID
    amount: Decimal
    currency: str
    settled_at: datetime
    source_occurrence_key: str | None
    related_resource_type: str | None
    related_resource_id: str | None
```

### Optional funding link (tax / reserve cycles)

```python
@dataclass(frozen=True)
class PlanningFundingLink:
    obligation_occurrence_key: str
    reservation_id: str
    funded_amount: Decimal
```

May start in `metadata` (`funds_occurrence_key`) before a first-class field.

---

## 4. Adapter protocol

```python
class PlanningSourceAdapter(Protocol):
    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution: ...

@dataclass(frozen=True)
class PlanningCollectionRequest:
    organization_id: UUID
    currency: str
    calculated_at: datetime
    period_start: datetime
    period_end: datetime

@dataclass(frozen=True)
class PlanningSourceContribution:
    source_name: str
    accounts: tuple[PlanningAccountSnapshot, ...] = ()
    cash_flows: tuple[PlanningCashFlow, ...] = ()
    reservations: tuple[PlanningReservation, ...] = ()
    settlements: tuple[PlanningSettlement, ...] = ()
    warnings: tuple[PlanningCollectionWarning, ...] = ()
    metadata: PlanningSourceMetadata | None = None
```

Each adapter emits **only** what it owns.

### Freshness metadata

```python
@dataclass(frozen=True)
class PlanningSourceMetadata:
    source_name: str
    collected_at: datetime
    data_as_of: datetime | None
    status: Literal["available", "partial", "unavailable"]
```

---

## 5. Accounts → liquidity

**Responsibility:** balances, currency, type, liquidity, eligibility, `balance_as_of`.  
**Not responsible for:** how much the user may spend.

Default eligibility:

| Type | Included |
|------|----------|
| cash, checking, savings, wallet / digital_wallet | Yes |
| investment, retirement, receivable, credit_card, loan, mortgage, property | No |

User overrides may come later via settings.  
Adapter: `AccountPlanningAdapter` + `AccountEligibilityPolicy` + `AccountPlanningQuery` port.

---

## 6. Transactions → settlements

Transactions do **not** invent future flows (unless explicit scheduled-tx feature exists later).

Primary role: prove what already happened — payments linked to commitments, goal transfers, tax payments, recurring confirmations, any tx with `planning_occurrence_key`.

Prefer **explicit** `planning_occurrence_key` on the transaction (or payment metadata) over heuristic match by amount/description/date. Heuristics → `possible_duplicate_cash_flow` warning only in V1 (no auto-drop).

Past transactions are **not** re-projected as future cash flows; they only reduce `outstanding_amount` via settlement reconciliation.

---

## 7. Commitments → required payments

Emit **all** payment occurrences in the horizon (not only `next_due_date`) — e.g. three mortgage dues in 90 days.

Certainty: typically `confirmed`. Category: `commitment`.

**Project:** active, overdue/defaulted, paused **when a contractual payment still exists**.  
**Do not project:** archived, closed with no pending balance, cancelled, paid off (display).

Paused ≠ cancelled obligation.

---

## 8. Goals → contributions and reservations

| `GoalFundingMode` | Cash flow | Reservation |
|-------------------|-----------|-------------|
| `informational` | — | — |
| `planned` | Future contributions | Does not auto-protect accumulated progress |
| `protected` | Optional separate contributions | Protects assigned balance |

Never double-discount the same pesos as both full reservation and full future contribution without distinct identities.

Linked accounts: put `linked_account_id` / `protection_scope` in metadata so protected amount cannot exceed that account’s available cash.

---

## 9. Taxes → reserves and dues

Two impacts:

1. **Reservation** — money that must stay protected (accrued/reserved)  
2. **Cash flow** — dated tax payment  

Anti double-count: pending reserve + payment for the same economic obligation share a funding link / `funds_occurrence_key`. Before due date, reserve protects cash; on payment date, reserve funds the outflow — **not** both full amounts subtracted independently.

If Taxes is incomplete: manual reserves/dues + warnings — **never invent estimates**.

---

## 10. Recurring → forecast occurrences

Recurring expands rules into dated occurrences. Planning **never** interprets recurrence expressions itself.

```text
Recurring occurrence = forecast
Posted transaction   = fact → settlement satisfies occurrence
```

Recurring does not auto-create transactions.

---

## 11. Manual planned cash flows (Planning-owned persistence)

Hypotheses entered in Planning (bonus, laptop purchase, one-off receipt) are **not** future transactions.

Persist `PlannedCashFlow` (Planning data). Projection remains ephemeral.

Statuses: `active` → `settled` (when linked to a transaction) | `cancelled` | `expired`.  
Avoid “completed” — the real fact is the Transaction.

---

## 12–13. Context builder & processing order

```text
1 Collect adapters
2 Normalize
3 Validate (org + currency)
4 Deduplicate
5 Reconcile settlements
6 Inclusion policies (8.2)
7 Chronological projection
8 Safe To Spend
9 Explanation
```

**Deduplicate before reconcile** — otherwise two duplicate sources can consume the same payment twice.

`PlanningContextBuilder` composes adapters + `PlanningCashFlowDeduplicator` + `PlanningSettlementReconciler`. Engine stays pure (no repos).

---

## 14. Deduplication strategy

1. **Exact `occurrence_key`** (authoritative)  
2. **Explicit resource link** (e.g. recurring bound to commitment — configure primary source)  
3. **Heuristic** (amount, currency, near dates) → warning only in V1  

Precedence when commitment and recurring represent the same payment:

```text
Commitment > Recurring
```

---

## 15. Settlement reconciliation

| Case | Result |
|------|--------|
| Full match | `outstanding = 0`, `settled` |
| Partial | reduce outstanding, `partially_settled` |
| Overpay | outstanding 0; excess stays in ledger balance (not a planning inflow) |

---

## 16. Calendar

Calendar is **not** an independent financial source. Events must be backed by Commitment / Recurring / Goal / Tax / PlannedCashFlow.

```text
Commitment occurrence → PlanningCashFlow → Calendar item
```

Never the reverse (avoids commitment + calendar reminder double count).

---

## 17. Timeline

Do **not** emit Timeline events on every Dashboard open / every calculation.

V1: on-demand calculation, **no** Timeline writes. Prepare event contracts for a later slice (material change detection / optional snapshot summary). Full `planning_projection_snapshots` table is **out of 8.3**.

---

## 18. Dashboard

Dashboard calls Planning’s public query — does **not** rebuild math.

```text
GET …/planning/safe-to-spend?currency=MXN&horizon=30_days
```

Summary fields only (`safe_to_spend`, `committed`, `reserved`, `status`, `confidence`, `calculated_at`). No knowledge of dedupe/settlements/policies inside Dashboard.

---

## 19–20. Tenant & multi-currency

Every contribution item must match `request.organization_id` (assert even if repos filter).  
One engine run = one currency. No FX. No global STS. No USD covering MXN deficit. Surfaces expose `selected_currency`.

Cross-currency transfer legs belong in **separate** contexts.

---

## 21. Partial adapter failures

Accounts + currency are **critical**.  
Taxes critical only if tax integration enabled for the org.  
Goals / Recurring may be empty validly.

Distinguish “no data” vs “could not fetch.” On partial failure: lower confidence, warnings (`tax_source_unavailable`), status `limited` or `insufficient_data` by severity.

---

## 22. Public read ports (no cross-module table joins)

```python
class AccountPlanningQuery(Protocol): ...
class CommitmentPlanningQuery(Protocol): ...
class GoalPlanningQuery(Protocol): ...
class TaxPlanningQuery(Protocol): ...
class RecurringPlanningService(Protocol): ...
class TransactionPlanningQuery(Protocol): ...
```

Preferred layout: adapters live under owning modules (`accounts/infrastructure/planning/`, …) implementing Planning ports. Planning domain only depends on ports.

Suggested Planning package shape: `domain/` (VOs, policies, services, ports) · `application/` · `infrastructure/adapters/` (wiring) · `api/`.

---

## 23. Initial HTTP surface (org-scoped, as elsewhere)

```text
GET /api/v1/organizations/{org_id}/planning/projection?currency=&horizon=
GET /api/v1/organizations/{org_id}/planning/safe-to-spend?currency=&horizon=
GET /api/v1/organizations/{org_id}/planning/sources?currency=&horizon=
```

`/sources` is diagnostic (per-source status, counts, warnings).

---

## 24. Cache & observability (prepare, light V1)

Cache key idea: `planning:{org}:{currency}:{horizon}:{context_version}` — invalidate on account/tx/commitment/goal/recurring/tax/settings/planned-flow changes. V1 may use short TTL (30–60s) if `calculated_at` is shown.

Metrics/logs: duration, source collection, deduped flows, matched settlements, failures — **no** sensitive notes/descriptions; amounts only if logging policy allows.

---

## 25. Cross-cutting decision: `occurrence_key`

Adopt **now** across Commitments, Recurring, scheduled Goals, Taxes, PlannedCashFlows, and linked Transactions.

Without stable identity, dedupe collapses to fragile amount/date matching. With it, partial payments and shifted dates still reconcile correctly.

---

## Acceptance criteria (8.3)

- [x] Planning consumes own contracts — not foreign ORM entities  
- [x] Accounts → liquidity snapshots per currency  
- [x] Transactions → settlements / evidence  
- [x] Commitments → multi-occurrence outflows + stable keys  
- [x] Goals → planned contributions vs protected reservations  
- [x] Taxes → reserve vs payment without double count  
- [x] Recurring → materialized occurrences (forecasts)  
- [x] Manual planned cash flows persistable as hypotheses  
- [x] Calendar not a financial source of truth  
- [x] Deduplicate before settlement reconcile  
- [x] Partial payments reduce outstanding  
- [x] Partial source failure → warnings + confidence impact  
- [x] Org + currency isolation validated  
- [x] Engine remains deterministic / repo-free  
- [x] Dashboard consumes public Planning API  
- [x] No automatic FX  

---

## Next

**8.4** — UX surfaces and “¿Qué pasa si…?” scenario shapes on top of this integration + 8.2 engine.
