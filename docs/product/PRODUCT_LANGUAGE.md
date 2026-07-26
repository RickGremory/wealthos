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

### Safe to Spend

Cash that can be used without breaking commitments, goals, or planned reserves.  
(Concept reserved for Planning — must stay consistent when introduced.)

### Cash Flow

Movement of money over a period (in vs out). Distinct from Net Worth (stock) vs flow.

### Financial Calendar

Dates that matter financially (due dates, statement days, estimated payoff) — **events**, not a todo app.

### Payment strategy

User preference for ordering obligations (`avalanche`, `snowball`, `manual`).  
Produces recommendations only; never mutates the ledger.

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

### Financial Timeline

Unified chronological spine of financial life (transactions, goals, commitments, calendar, taxes, planning). Not a social feed; not a second ledger. Concept reserved — see [decision](../decisions/2026-07-25-financial-timeline.md).

---

## Module questions (product map)

| Module | Answers |
|--------|---------|
| Accounts | ¿Dónde está mi dinero? |
| Transactions | ¿Qué ocurrió con mi dinero? |
| Dashboard | ¿Cómo está mi salud financiera? |
| Goals | ¿Qué estoy construyendo? |
| Financial Commitments | ¿Qué parte de mi futuro ya está comprometida? |
| Planning | ¿Qué puedo hacer el próximo mes? |
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
| Financial Timeline | Future composition surface — not a module table yet |

---

## Phrases we prefer

| Prefer | Avoid |
|--------|--------|
| Obligaciones / Financial Commitments | “Debts” as the only nav label |
| `/app/commitments` | `/app/debts` in new UI |
| El saldo viene de la cuenta | “Balance de la deuda” as stored field |
| New Payment → Transfer flow | “Make Payment” engine aparte del ledger |
| What should I do next? | Solo métricas sin orientación |
| Compromiso financiero | “Pasivo genérico” in user-facing copy when we mean a managed obligation |

---

## Status

Living document. Update when a new product noun becomes load-bearing.
