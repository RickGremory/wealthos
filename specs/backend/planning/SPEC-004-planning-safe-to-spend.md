# SPEC-004

# Planning & Safe To Spend — End-to-End Implementation

| Field | Value |
|-------|-------|
| **Status** | Completed |
| **Author** | Ricardo Balam |
| **Created** | 2026-07-25 |
| **Parent Epic** | [EPIC-007](../../../docs/epics/EPIC-007-planning-safe-to-spend.md) |
| **Parent RFC** | [RFC-004](../../../docs/rfc/RFC-004-planning-projection.md) |
| **Design pillars** | [8.1](../../../docs/roadmap/sprint-8.1-planning-domain-model.md)–[8.4](../../../docs/roadmap/sprint-8.4-planning-ux-scenarios.md) |
| **Detail brief** | [Sprint 8.5](../../../docs/roadmap/sprint-8.5-implementation-spec.md) |

> Once **Completed**, this SPEC is immutable. Further changes require a new SPEC.  
> Existing `modules/planning/` (budgets / cash plans) remain tools; this SPEC elevates **Financial Projection / Safe To Spend** as the product spine.

---

## 1. Objective

Ship Planning so a user can:

1. Configure org Planning settings (horizon, safety reserve, certainty toggles)  
2. Register manual planned inflows/outflows  
3. See **Disponible para usar** for a currency + horizon with status, confidence, breakdown, alerts  
4. Simulate “what if?” without mutating real data  
5. See the same summary on Dashboard  

via `calculate_projection(context)` — Safe To Spend is a **result field**, not a stored ledger value.

---

## 2. Scope

### Included

- `PlanningSettings` + `PlannedCashFlow` persistence + Alembic  
- Immutable Planning DTOs / VOs  
- Policies: eligibility, inclusion, ordering, reserve, STS, status, confidence  
- Services: context builder, deduplicator, settlement reconciler, projection engine, explainer, scenario engine  
- Adapters (ports): accounts, transactions, commitments, goals, taxes, recurring (empty OK), manual  
- APIs: projection, safe-to-spend summary, sources, settings, planned cash flows, simulate  
- UI: `/app/planning`, `/app/planning/settings`, scenario builder  
- Dashboard Safe To Spend card  
- Unit / integration / E2E critical paths  

### Out of scope

- Persist scenarios · AI · FX · bank sync · projection snapshots · Timeline auto-events · complex refinance · probabilistic models  
- Recurring occurrence expansion (stub until Sprint 9)  
- Full tax engine inside Planning  

---

## 3. Architecture

```text
UI Planeación (/app/planning) + Dashboard summary
        │
        ▼
GET/POST …/organizations/{id}/planning/*
        │
        ▼
application queries/commands
        │
        ├──► PlanningContextBuilder + adapters (ports)
        │         ↓
        └──► PlanningProjectionEngine (pure)
                    ↓
              PlanningProjectionResult
                    └── safe_to_spend, timeline, alerts, …
```

**Invariants:** Decimal money · one currency per run · org isolation · no foreign ORM in engine · dedupe before reconcile · trough-based STS · `null` ≠ zero for insufficient data · simulations never persist · frontend never recomputes math.

---

## 4. Persistence (only)

### `planning_settings`

| Column | Notes |
|--------|--------|
| `id`, `organization_id` UNIQUE | one row per org |
| `default_horizon` | default `30_days` |
| `safety_reserve_strategy` | `none` \| `fixed_amount` \| `linked_goal` (V1) |
| `safety_reserve_amount` | NULL or ≥ 0 |
| `linked_emergency_goal_id` | soft ref; validate via Goals port |
| `include_expected_income` | default true |
| `include_estimated_expenses` | default true |
| `version`, `created_at`, `updated_at` | optimistic concurrency |

### `planned_cash_flows`

| Column | Notes |
|--------|--------|
| `id`, `organization_id`, `name` | |
| `direction` | inflow \| outflow |
| `amount` | Numeric(19,4) > 0 |
| `currency`, `expected_at` | indexed with org |
| `certainty`, `status` | active \| settled \| cancelled \| expired |
| `notes`, `settled_transaction_id` | |
| `version`, timestamps | |

Indexes: `(organization_id, currency, expected_at)`, `(organization_id, status)`.

**Do not create tables for:** `safe_to_spend`, projections, scenarios, breakdowns.

---

## 5. Domain enums (V1)

`PlanningHorizon`: `today` \| `7_days` \| `30_days` \| `90_days`  
`CashFlowDirection` / `CashFlowCertainty` / `CashFlowStatus`  
`ProjectionStatus`: healthy \| limited \| zero \| deficit \| insufficient_data \| unavailable  
`ProjectionConfidence`: high \| medium \| low  
`SafetyReserveStrategy`: none \| fixed_amount \| linked_goal (+ stubs for % / days)

Money: `Decimal` only; API strings; quantize via central money policy (2 dp for MXN/USD/EUR today).

Horizon resolve uses **org timezone** for “today” — not naive UTC.

---

## 6. Engine pipeline

```text
Collect adapters (stable order: accounts → transactions → commitments → goals → taxes → recurring → manual)
→ Normalize / validate org+currency
→ Deduplicate (occurrence_key; Commitment > Tax > Goal > Planned > Recurring)
→ Reconcile settlements (explicit occurrence_key only)
→ Inclusion policies
→ Chronological order (same-day: outflows before inflows)
→ ProjectionPoints (t0 + events)
→ Safety reserve
→ SafeToSpend (max(0, min_balance − reserve); distinguish cash_deficit vs reserve_shortfall)
→ Status / confidence / alerts / explanations
```

### Safe To Spend

```text
amount = max(0, minimum_projected_balance − required_reserve)
reserve_shortfall when min < reserve (even if cash > 0)
status deficit when min < reserve (not only when min < 0)
```

`safe_to_spend = null` for `insufficient_data` / `unavailable`.

### Confidence

Internal score → label only (`high`/`medium`/`low`) + reason codes — never fake %.

### Recurring / Taxes V1

Recurring adapter: empty `available` contribution until Sprint 9.  
Taxes: manual reserves/dues or `partial` — never invent ISR/IVA inside Planning.

---

## 7. API (org-scoped)

```text
GET  /api/v1/organizations/{org_id}/planning/projection
GET  /api/v1/organizations/{org_id}/planning/safe-to-spend
GET  /api/v1/organizations/{org_id}/planning/sources
GET  /api/v1/organizations/{org_id}/planning/settings
PUT  /api/v1/organizations/{org_id}/planning/settings
GET  /api/v1/organizations/{org_id}/planning/cash-flows
POST /api/v1/organizations/{org_id}/planning/cash-flows
PATCH/DELETE …/cash-flows/{id}   # DELETE = cancel
POST /api/v1/organizations/{org_id}/planning/scenarios/simulate
```

Auth: membership; cross-tenant → 404. No cache required for V1 (measure first).

Simulate adjustments V1: `add_cash_flow` (in/out); contract may include remove/replace/change_reserve. Temporary keys `scenario:{adjustment_id}`.

---

## 8. Frontend

Routes: `/app/planning`, `/app/planning/settings` · nav **Planeación**.  
Types: money as string. Composables: `usePlanningProjection`, `usePlanningScenario`, `usePlanningSettings`.

MVP components: hero, horizon, summary, upcoming, breakdown, alerts, scenario builder/comparison, empty. Chart can follow textual MVP.

Cuts: (1) route+hero (2) summary/flows/breakdown/alerts (3) settings+manual CF (4) scenarios (5) chart+a11y+responsive.

Dashboard uses **summary DTO only**. Privacy hide-amounts applies.

---

## 9. Phases / DoD checklist

| Phase | Deliverable | Done when |
|-------|-------------|-----------|
| 1 | Foundation | Migration + settings + planned CF repos |
| 2 | Engine | Policies + ProjectionEngine + unit tests (acceptance fixtures) |
| 3 | Integration | Adapters + dedupe + reconcile + context builder tests |
| 4 | API | All endpoints + OpenAPI |
| 5 | UI base | Planning page hero → alerts |
| 6 | Scenarios | Simulate API + UI comparison |
| 7 | Dashboard + polish | Card, privacy, E2E, SPEC → Completed |

### Acceptance fixtures (must pass)

1. Classic: 50k −12k −6.3k +30k, reserve 10k → STS **21_700**, healthy  
2. Rent before payroll: STS **0**, zero (income after trough)  
3. Reserve shortfall without negative cash → deficit + `reserve_shortfall`  
4. No eligible accounts → `insufficient_data`, `safe_to_spend: null`  

### Sprint DoD

- [ ] Org settings + manual planned flows  
- [ ] Per-currency / horizon projection  
- [ ] Liquid cash only; chronological trough; configured reserve  
- [ ] No double-count; total/partial settlements  
- [ ] Facts vs forecasts; confidence; alerts; inclusions/exclusions explained  
- [ ] Scenarios reuse engine; no real mutation  
- [ ] Dashboard summary; UI separates current / available / projected  
- [ ] Critical tests green; no FX; STS not persisted  

---

## 10. Suggested module layout

Elevate under `modules/planning/` with `domain/` (entities, enums, VOs, policies, services, ports), `application/`, `infrastructure/` (persistence + adapters or wire owning-module adapters), `api/`.

Owning modules may host `infrastructure/planning/` adapters implementing Planning ports.

---

## 11. Observability

Structured logs without sensitive notes/names. Metrics: projection duration, adapter duration, flows collected/deduped, settlements matched, failures. Timeline material-change event contract **defined but not published**.

---

## 12. Commit / PR convention

`feat(planning): …` · `test(planning): …` · `feat(dashboard): wire safe-to-spend summary`
