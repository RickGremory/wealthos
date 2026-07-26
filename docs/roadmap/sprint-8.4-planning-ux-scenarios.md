# Sprint 8.4 — Planning UX & “What if?” scenarios

**Status:** Accepted  
**Parent:** [Sprint 8](./sprint-8-planning-safe-to-spend.md)  
**Depends on:** [8.1](./sprint-8.1-planning-domain-model.md) · [8.2](./sprint-8.2-safe-to-spend-algorithm.md) · [8.3](./sprint-8.3-planning-integration.md)  
**Next:** 8.5 — Technical SPEC + implementation

> **Frozen UX / scenario contract.** Turns Planning into a decision surface the user can trust in seconds — without exposing engine internals.  
> No application code in this slice.

---

## Objective

Convert the Planning calculation into an experience that is **clear, trustworthy, and useful**.

Avoid two extremes:

1. A single unexplained number  
2. An overly technical financial report  

### Product rule

```text
In a few seconds the user must understand:
how much they can use, what is protected, and what could go wrong.
```

### Three numbers that must never be confused

| Concept (ES) | Meaning |
|--------------|---------|
| **Saldo actual** | Liquid cash included now |
| **Disponible para usar** | Safe To Spend for the horizon |
| **Saldo proyectado** | Balance after future events (e.g. ending / chart) |

Example: 50_000 current ≠ 21_700 spendable ≠ 57_700 projected ending.

---

## 1–3. Route, naming, page structure

| | |
|--|--|
| Route | `/app/planning` |
| Nav label | **Planeación** |
| Not primary name | “Safe To Spend” (capability inside Planning) |

Header question:

> ¿Cuánto puedo usar sin comprometer mis próximos pagos?

Page IA:

```text
Planning
├── Resumen principal
├── Selector de horizonte
├── Estado y confianza
├── Próximos movimientos
├── Desglose del cálculo
├── Escenario “¿Qué pasa si...?”
├── Alertas / Requiere atención
└── Configuración (separate route)
```

Visual order: **Result → What’s coming → Why → What if → Needs attention**.

Settings: `/app/planning/settings` (not cluttering the main page).  
Scenarios: may live on `/app/planning` in V1; optional `/app/planning/scenarios` later.

---

## 4–5. Header & horizon

Always show **currency** (e.g. “Planeación en MXN”). Multi-currency note: amounts are **only** that currency — never a global total.

Horizons: **Hoy · 7 días · 30 días · 90 días** (segmented desktop / compact mobile).

On change: recalculate result, upcoming, trough, alerts; keep currency; reset or recompute active scenario.  
**Do not** mutate `PlanningSettings.default_horizon` from a temporary UI change.

Prudent copy under the hero:

> Según los saldos, pagos, metas y reservas registrados.

Never: “Puedes gastar con total seguridad.”

---

## 6–8. Hero card, status, confidence

Hero: **Disponible para usar** + amount + horizon + status + confidence + one-line trough/reserve hint.

Statuses (text + icon + label + description — not color alone):  
`healthy` · `limited` · `zero` · `deficit` · `insufficient_data` · `unavailable`

Confidence: **Alta / Media / Baja** with plain language — **no** fake percentages (“87%”).

---

## 9–11. Money summary & projection chart

Three blocks: **Efectivo disponible · Dinero comprometido · Fondos protegidos** (+ optional expected income).

Product language: **fondos protegidos** (domain may still say reservation).

Simple projected-balance chart: dates × balance; reserve line; trough marker; deficit date; inflow/outflow marks. Point selection shows that day’s flows.

Surface the temporal truth in copy when relevant:

> Tienes X hoy, pero la renta y la tarjeta se pagan antes de tu próximo ingreso.

---

## 12–14. Upcoming, breakdown, exclusions

**Próximos movimientos** — chronological list (not a heavy table): date, label, signed amount, certainty/protection badge. Open source module; show inclusion reason; scenario-only exclude — no silent edit of foreign resources.

**Cómo se calculó** — breakdown with included / not included rows (e.g. estimated income excluded). Collapsed by default on Dashboard widget; open on Planning.

**Datos no incluidos** — reasons (investment account, estimated income, informational goal). Not titled “Errores”.

---

## 15–21. Scenarios (“¿Qué pasa si…?”)

Second core capability. Header: **Simular una decisión**.

V1 types:

1. Hypothetical expense  
2. Hypothetical income  
3. Bring a payment forward  
4. Change a goal contribution  

Forms: amount, currency (must match projection), date, optional category/description.

### Narrative rules

- Show **baseline vs simulated** (available, trough, status, reserve, deficit date).  
- Risk: deficit amount + date + “try after payday” — **no moralizing**.  
- Income after trough: may **not** raise today’s Safe To Spend — explain why.  
- Advance payment: must **satisfy/replace** the existing occurrence (same engine), not naively subtract twice.  
- Goal contribution change: STS delta in Planning; goal completion estimate from **Goals**, not reimplemented.

---

## 22–25. Scenario model & isolation

```ts
interface PlanningScenario {
  id: string
  name: string | null
  organizationId: string
  currency: string
  horizon: PlanningHorizon
  adjustments: ScenarioAdjustment[]
  baseline: PlanningResult
  simulated: PlanningResult
  createdAt: string
}
```

V1: request-scoped only (no persist). Permanent banner: **Modo simulación — ningún dato real será modificado.** Exit: **Descartar simulación** (not “Guardar” unless creating a real entity).

```ts
type ScenarioAdjustment =
  | AddCashFlowAdjustment
  | RemoveCashFlowAdjustment
  | ReplaceCashFlowAdjustment
  | ChangeReservationAdjustment
```

Convert to real action only via explicit confirmed flows: create PlannedCashFlow, navigate to Goals, open payment/transfer.

---

## 26–29. Comparison, reason codes, materiality

Side-by-side (cards on mobile): available, ending, trough, protected, status, confidence, deficit date.

API returns **reason codes**; frontend owns copy:

`scenario_reduces_safe_to_spend` · `scenario_creates_deficit` · `scenario_preserves_commitments` · `scenario_breaks_safety_reserve` · `scenario_delays_goal` · `scenario_income_arrives_after_low_point` · `scenario_replaces_existing_outflow` · `scenario_has_no_material_impact` · `scenario_currency_mismatch`

Material change policy: absolute/relative thresholds, status change, new deficit, reserve breach — ignore 1 MXN noise.

---

## 30–31. Multi-currency & same-currency transfers

One scenario = one currency. No USD purchase inside MXN projection (switch currency or separate simulation). No FX.

Same-currency internal transfer: usually no change to total available unless moving included↔excluded or into protected/liquidity constraints. Cross-currency transfer: block or split until FX exists.

---

## 32–36. Alerts, attention, settings

Alerts after hero: Critical → Warning → Info, with actions when possible.

**Requiere atención** — only actionable items (not every technical warning).

Settings (`/app/planning/settings`): default horizon, minimum reserve (none / fixed / emergency goal), included accounts, expected-income & estimated-expense toggles. V1 UI for reserve: **not** % of cash / days of expenses yet (domain ready).

Including investments: warn that money may not be immediately liquid.

---

## 37–42. Empty / loading / error / responsive / a11y / privacy

Empty: no liquid accounts; no future flows (still compute with note); no reserve (CTA); empty commitments/recurring = valid.

Loading: skeletons — not “consultando adaptadores”.

Errors: impossible (e.g. accounts down) vs partial (e.g. taxes missing).

Mobile order: Result → Horizon → Status → Summary → Alerts → Flows → Scenario → Breakdown. No wide tables.

A11y: not color-only; amount announcements; chart text summary; scenario as simulation; `aria-live` on impact.

Global hide-amounts applies to Planning (hero, chart, lists); keep status/confidence/dates/labels per product policy.

---

## 43–45. APIs (org-scoped)

```text
GET  /api/v1/organizations/{org_id}/planning/projection?currency=&horizon=
POST /api/v1/organizations/{org_id}/planning/scenarios/simulate
```

Projection payload includes: status, confidence, safe_to_spend, cash/income/committed/protected, min & ending balances, lowest_balance_at, timeline, breakdown, alerts, excluded_items, source_summary.

Simulate: adjustments → `{ baseline, simulated, impact }` with deltas + reason_codes.

**Frontend never recomputes** Safe To Spend / trough / deficit / confidence — same backend engine as Dashboard.

---

## 46–48. Frontend shape

Suggested: `components/planning/*` (hero, horizon, badges, summary, chart, flows, breakdown, excluded, alerts, scenario builder/comparison/narrative, empty).

Composables: `usePlanningProjection`, `usePlanningScenario`, `usePlanningSettings`, currency/horizon helpers.

Cache key: `planning-projection:{org}:{currency}:{horizon}` — invalidate on account/tx/commitment/goal/recurring/planned/settings writes. **Simulation never overwrites baseline cache.**

---

## 49–52. Dashboard, Calendar, Timeline, analytics

Dashboard widget → deep-link `/app/planning?horizon=&currency=`. Deficit shows amount + date (never hide behind bare zero).

Calendar: “Ver en calendario” — same occurrence keys, no duplicate events.

Timeline: no events on every query in this phase; prepare for later material events.

Product analytics (no amounts/names/notes): page view, horizon change, breakdown open, scenario start/simulate/discard/convert, alert action, settings open — with horizon, currency code, status, confidence, scenario type, deficit boolean, source count.

---

## Acceptance criteria (8.4)

- [x] Main Planning page + nav **Planeación**  
- [x] Hero shows currency + horizon + status + confidence  
- [x] Cash / committed / protected visible  
- [x] Chronological upcoming + calculation explanation  
- [x] Exclusions show reasons  
- [x] Deficits show amount + date  
- [x] Simulate spend/income (+ advance pay / goal contribution in V1 set)  
- [x] Baseline vs simulated comparison  
- [x] Simulation never mutates real data  
- [x] Same backend engine for projection & scenarios  
- [x] Reason codes for impact narrative  
- [x] Mobile without wide tables  
- [x] Global privacy hides amounts  
- [x] Dashboard reuses public Planning result  
- [x] No implicit FX / currency mixing  
- [x] Three-number distinction (current / spendable / projected) documented  

---

## Next

**8.5** — SPEC + implementation (engine, adapters, APIs, Vue, tests) against 8.1–8.4.
