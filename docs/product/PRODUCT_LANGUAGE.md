# Product Language

Official vocabulary of WealthOS.

This is not a technical schema dump. It is the dictionary we use in product, code names where they must match, docs, AI, and marketing — so the product keeps one voice.

**Related:** [Product Principles](./02-product-principles.md) · [RFC-002](../rfc/RFC-002-financial-commitments.md)

---

## How to use this file

1. Prefer these terms in UI copy and docs.  
2. If a new concept appears, add it here **before** it spreads across modules.  
3. Backend package names may stay narrower (e.g. `debts/`) when the product term is broader (`Obligaciones`).

---

## Core terms

### Organization

The tenant workspace. Every financial record belongs to an Organization.

Answers: *Whose books are these?*

### Account

A container where money lives or is owed (asset or liability).

Answers: *¿Dónde está mi dinero?* (and for liabilities: *dónde vive el saldo de lo que debo*)

### Transaction

An immutable movement of money. The only way balances change.

Answers: *What moved, when, and why?*

### Category

A classification of income/expense transactions. Never a second ledger.

### Goal

A destination for money (home, runway, wealth). Goals **never own money**; progress is derived.

Answers: *¿Qué estoy construyendo con mi dinero?*

### Financial Commitment (*Compromiso financiero* / UI: **Obligaciones**)

Something that already claims future money.

Answers: *¿Qué compromete mi dinero futuro?*

First implemented type: **Debt**. Later: tax obligations, scheduled payments, etc.

### Debt

A Debt is a Financial Commitment backed by exactly one **liability Account**.  
Metadata and lifecycle only — **not** a stored balance.

### Liability

Account classification for money owed. Feeds Net Worth as the subtractive side.

### Asset

Account classification for money owned. Feeds Net Worth as the additive side.

### Net Worth

```text
Assets − Liabilities = Net Worth
```

Always explainable back to accounts (and thus transactions). No silent FX across currencies.

### Financial Truth

Every displayed amount can be explained from the source of truth (usually transactions → accounts).  
Never invent a convenient number.

### Safe to Spend (*Disponible para usar*)

Cash that can be used in a horizon without breaking commitments, goals, tax set-asides, or the safety reserve.

**Not a balance.** Consequence of a **Financial Projection**. Always shown with currency, horizon, status, confidence, and — on Planning — contrasted with **Saldo actual** and **Saldo proyectado**.

Product module surface: **Planeación** (`/app/planning`). Safe To Spend is a capability, not the nav name.

Answers: *¿Cuánto puedo usar sin comprometer mis próximos pagos?*

See [RFC-004](../rfc/RFC-004-planning-projection.md) · [Sprint 8.4](../roadmap/sprint-8.4-planning-ux-scenarios.md) · [Principle 10](./02-product-principles.md).

### Fondos protegidos

Product term for money that should not be spent (goals, taxes, safety). Domain may say *reservation*; UI prefers **protegidos**.

### Planeación (module)

UI route `/app/planning` · settings `/app/planning/settings`. Hosts projection, upcoming flows, breakdown, alerts, and **¿Qué pasa si…?** simulations.

### Financial Projection

Computed photograph of the future for one org, currency, and horizon (today / 7d / 30d / 90d). Ephemeral — not persisted. Orchestrated by Planning from other modules’ facts and forecasts.

### Money states (Planning)

| ES | Meaning |
|----|---------|
| Disponible | May still be used (spendable slice) |
| Comprometido | Known future claim (obligations, fixed outflows) |
| Reservado | Should not touch (tax, goals, safety) |
| Gastado | Already occurred (ledger facts) |

### Facts vs Forecasts

| | |
|--|--|
| **Fact** | Confirmed (balances, posted transactions, existing commitments) |
| **Forecast** | Projected (expected income, future payments, planned savings) |

Projections must expose the mix for trust and future AI confidence.

### Cash flow certainty (Planning)

| Level | Meaning | Safe To Spend (V1) |
|-------|---------|-------------------|
| `confirmed` | Strong evidence | Include |
| `expected` | Reasonably likely | Income if settings allow (default on); outflows include |
| `estimated` | Weak forecast | Income **excluded**; outflows may include conservatively |

Uncertain income must not inflate spendable cash.

### Goal funding mode (Planning)

| Mode | Effect |
|------|--------|
| `informational` | Progress only — no STS reduction |
| `planned` | Dated contribution reduces STS |
| `protected` | Linked cash treated as reserved |

### Occurrence key (Planning)

Stable identity for an expected movement across modules, e.g. `commitment:{id}:due:2026-08-15` or `recurring:{rule_id}:occurrence:2026-08-15`.

Used to dedupe forecasts and to link **Transactions** (settlements) to projected outflows — including partial payments. Preferred over matching by amount/date alone.

For Recurring, the key uses the **original** expected date even after a single-occurrence reschedule.

See [Sprint 8.3](../roadmap/sprint-8.3-planning-integration.md) · [Sprint 9.1](../roadmap/sprint-9.1-recurring-domain-model.md).

### Movimiento recurrente (*RecurringRule*)

Persistent configuration for a repeating expected inflow, outflow, or transfer (salary, rent, subscription, savings transfer).

Product: **Movimiento recurrente**. Code: series shell `RecurringRule` + temporal `RecurringRuleVersion` (config never flattened only onto the shell).

Answers: *¿Qué movimientos espero que se repitan?*

Structural mid-series changes (“desde septiembre, 950 MXN”) create a new version with `effective_from` — history is not rewritten.

Not a Transaction. Not proof that money moved. See [Principle 11](./02-product-principles.md) · [RFC-005](../rfc/RFC-005-recurring-engine.md) · [Sprint 9.3](../roadmap/sprint-9.3-persistence-lifecycle.md).

### Recurring occurrence (*ocurrencia proyectada*)

A calculated instance of a RecurringRule for a date — amount, direction, certainty, derived status. Generated on demand for a period; not mass-persisted as future rows.

### Pendiente de confirmar (Recurring overdue UX)

When an expected occurrence’s date passed without a linked Transaction, domain status may be `overdue`. UI prefers **Pendiente de confirmar** — expectation without confirmation, not contractual default.

### Omitida (skipped occurrence)

User marked that instance as not expected. Planning excludes it from active upcoming payments.

### Planned cash flow (manual)

A user-entered hypothesis in Planning (future inflow/outflow). Persisted; not a ledger transaction. Settled when linked to a real Transaction.

### Cash Flow

Movement of money over a period (in vs out). Distinct from Net Worth (stock) vs flow.

### Financial Calendar

Dates that matter financially (due dates, statement days, estimated payoff) — **events**, not a todo app.

### Payment strategy

Organization-level preference (`avalanche` | `snowball` | `minimum_only` | `manual`) that **ranks and explains** which obligation to prioritize. Never creates transactions. See [Sprint 6.4](../roadmap/sprint-6.4-payment-strategies.md).

### Minimum payment vs scheduled payment

- **Minimum payment** — typically credit cards (variable floor).  
- **Scheduled payment** — mortgages / MSI / installment contracts.  

ViewModels may collapse to `required_payment` + `required_payment_type`; the domain keeps both.

### Settled (paid currently)

Revolving commitment with zero balance **now**, still open to new charges. Distinct from permanent **paid off** / **closed**.

---

### Emotional priority

User-chosen High / Medium / Low on a commitment.

### Financial priority

System-derived ranking (rates, balances, dues) for recommendations — separate from emotional priority.

### Next Action (*What should I do next?*)

A single orienting sentence on a commitment (and later Goals / Taxes / Planning) that tells the user the most useful next step.

Not a task system. Not a second ledger. Pure guidance copy derived from existing data (due date, minimum, status).

See [Sprint 6.2 UX](../roadmap/sprint-6.2-commitments-ux.md).

### Overdue (UX state)

Derived when a due date has passed and the commitment still has a balance. Shown with danger emphasis. Distinct from domain status `defaulted`.

### Needs Attention

Dashboard (and similar surfaces) attention items derived from commitments and other domains — e.g. overdue payment. Never a stored column on Debt.

### Financial Timeline / Historia

Unified chronological spine of financial life (transactions, goals, commitments, calendar, taxes, planning). Not a social feed; not a second ledger. Product surface: **Historia** at `/app/timeline`. See [decision](../decisions/2026-07-25-financial-timeline.md) and [SPEC-003](../../specs/backend/timeline/SPEC-003-financial-timeline.md).

---

## Module questions (product map)

| Module | Answers |
|--------|---------|
| Accounts | ¿Dónde está mi dinero? |
| Transactions | ¿Qué ocurrió con mi dinero? |
| Dashboard | ¿Cómo está mi salud financiera? |
| Goals | ¿Qué estoy construyendo? |
| Financial Commitments | ¿Qué parte de mi futuro ya está comprometida? |
| Planning | ¿Qué puedo hacer el próximo mes? / ¿Cuánto puedo gastar con tranquilidad? |
| Recurring | ¿Qué movimientos espero que se repitan? |
| Taxes | ¿Qué debo reservar al gobierno? |
| Financial Timeline | ¿Qué ha pasado en mi vida financiera, en orden? |

## Naming map (product ↔ code)

| Product (ES / EN) | Code / module |
|-------------------|---------------|
| Organización | `Organization` |
| Cuenta | `Account` |
| Movimiento / Transacción | `Transaction` |
| Meta | `Goal` |
| Obligaciones / Financial Commitments | UI routes `/app/commitments`; domain `modules/debts/` |
| Deuda (tipo de obligación) | `Debt` aggregate |
| Patrimonio neto | Net Worth (Dashboard projection) |
| Verdad financiera | Principle + invariant, not a table |
| ¿Qué debo hacer ahora? / Next Action | Guidance section — not persisted as tasks |
| Historia / Financial Timeline | UI `/app/timeline`; module `modules/timeline/`; contract `shared/events/` |
| Disponible para usar / Safe To Spend | Consequence of `PlanningProjection`; UI under **Planeación** |
| Planeación | UI `/app/planning`; module `modules/planning/` |
| Movimiento recurrente / RecurringRule | UI (planned) Movimientos recurrentes; module `modules/recurring/` |
| Ocurrencia proyectada | Calculated VO — not mass-persisted futures |
| Fondos protegidos | Product label for reservations |
| Financial Projection | Computed view — not a table; see RFC-004 |

---

## Phrases we prefer

| Prefer | Avoid |
|--------|--------|
| Obligaciones / Financial Commitments | “Debts” as the only nav label |
| `/app/commitments` | `/app/debts` in new UI |
| El saldo viene de la cuenta | “Balance de la deuda” as stored field |
| Disponible para usar + por qué | Solo un número sin explicación |
| Saldo actual ≠ Disponible ≠ Proyectado | Un solo “saldo” ambiguo |
| Fondos protegidos | “Reservado” genérico en UI |
| Modo simulación / Descartar | Guardar implícito de un what-if |
| Disponible / Comprometido / Protegido | “Saldo” como si fuera gastable |
| What should I do next? | Solo métricas sin orientación |
| Compromiso financiero | “Pasivo genérico” in user-facing copy when we mean a managed obligation |
| Expectativa / previsión recurrente | “Ya se pagó” because a recurrence exists |
| Pendiente de confirmar | “Vencida / deuda” for informative recurring gaps |
| Confirmar movimiento | Auto-crear transacciones desde un cron |

---

## Status

Living document. Update when a new product noun becomes load-bearing.
