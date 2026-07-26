# RFC-002

# Financial Commitments — Debt Product Model

**Author:** Ricardo Balam  
**Status:** Accepted  
**Created:** 2026-07-25  
**Sprint slice:** 6.1 — Domain / Product Model  
**Baseline:** `v0.5.0-foundation`

> **Frozen as product contract.** This RFC defines the language and invariants of Debts as the first **Financial Commitment**.  
> Do not invent balances, “manual payments,” or UI jargon that contradicts this document.  
> Execution continues via [EPIC-005](../epics/EPIC-005-debts.md) and Sprint 6 SPECs.  
> See [PRODUCT_LANGUAGE.md](../product/PRODUCT_LANGUAGE.md) and [Product Principles](../product/02-product-principles.md).

---

## Summary

WealthOS does not build a “debt tracker” as an isolated ledger.

It makes **financial commitments** visible: money that already has a claim on the user’s future.

Internally, the first commitment type lives in `modules/debts/`.  
In the product UI, users see **Obligaciones** (Financial Commitments) — not a technical aggregate name.

```text
Financial Commitment (product concept)
│
├── Debt                    ← Sprint 6 (this RFC)
├── Tax Obligation          ← later (Taxes)
├── Scheduled Payment       ← later
├── Subscription            ← optional later
└── Future Liability        ← later
```

---

## Motivation

After the foundation loop (accounts → transactions → dashboard → goals), the unanswered question is:

> ¿Qué compromete mi dinero futuro?

Accounts answer *where money is*.  
Commitments answer *what already owns tomorrow’s cash*.

Without liabilities, Net Worth is inflated. Debts also unlock richer Dashboard, Goals trade-offs, Planning, and AI — without changing the Net Worth formula itself.

---

## Goals

- One product model for any obligation kind (family loan → mortgage)
- Balance always from the liability **Account**
- Payments always via **Transactions**
- Enrich Dashboard / calendar / strategies without duplicating money
- Leave room for Taxes and other commitment types without renaming the UI concept

## Non-goals (Sprint 6)

- Refinancing / consolidation
- Amortization engines (French / German)
- Advanced compound interest
- Credit score
- Bank import
- AI recommendations (consume this model later)
- Vue screens in slice 6.1 (product model only)

---

## Principles applied

| Principle | How it shows up here |
|-----------|----------------------|
| Financial Truth | No `Debt.current_balance` field |
| One Source of Truth | Account (+ transactions) owns money |
| Money Always Moves | Paying = transfer / payment transaction |
| Financial Commitments | UI organizes obligaciones; backend module is `debts` |
| Planning Before Automation | Strategies are preferences, not silent mutations |

---

## 1. What a Debt is

A **Debt** is a **financial obligation** — metadata and lifecycle around a liability account.

It is **not**:

- A loan product from a bank’s perspective
- A bank entity
- A credit card plastic
- A second wallet of money

Examples (all `Debt`):

| Product type | `debt_type` |
|--------------|-------------|
| Credit card | `credit_card` |
| Mortgage | `mortgage` |
| Auto loan | `auto_loan` |
| Personal loan | `personal_loan` |
| Business loan | `business_loan` |
| Student loan | `student_loan` |
| Line of credit | `line_of_credit` |
| Family loan | `family_loan` |
| Installment / MSI | `installment_plan` |
| Other | `other` |

---

## 2. Single source of truth

```text
Debt
  │  (1:1 contract / metadata)
  ▼
Liability Account
  │  (holds signed balance)
  ▼
Transactions
  │  (only way money moves)
```

**Invariant:** `Debt.current_balance` does **not** exist as stored state.

Display balance is always derived from the linked liability account (typically shown as a positive “amount owed” from a negative liability balance).

---

## 3. Debt always lives on an account

- Every Debt has **exactly one** liability Account (`classification = liability`).
- A Debt cannot exist without that account.
- Archiving a Debt does **not** delete the account (and vice versa).

---

## 4. Creditor

Every Debt has a **creditor** — a descriptive string, not a system Contact.

Examples: HSBC, BBVA, Mercado Pago, INFONAVIT, Papá, Empresa XYZ.

---

## 5. Lifecycle status

| Status | Meaning |
|--------|---------|
| `active` | Can receive payments |
| `paid_off` | Balance is zero; no further payments until revived |
| `paused` | Temporarily not being paid; **not** the same as default |
| `defaulted` | User acknowledges breach; useful for future reporting |
| `archived` | Hidden from primary flows; history retained forever |

### Auto close / revive

**Refined by [settled vs paid off](../decisions/2026-07-25-settled-vs-paid-off.md) (Sprint 6.4):**

- **Revolving** (credit card, line of credit): balance → 0 means **settled / paid currently**, not permanent `paid_off`. Product stays open until closed; new charges revive activity without a false “debt finished forever” signal.
- **Installment loans** (mortgage, auto, personal, …): `paid_off` when balance = 0 **and** (liability account closed **or** user confirmation). Avoid auto-close on a temporary zero from an adjustment error.
- If an open liability balance becomes non-zero again, the commitment is active again (unless `archived`).

Manual status changes (pause / default / archive) are user intent; they must not invent balances.

---

## 6. Required vs optional fields

### Required (minimal)

| Field | Notes |
|-------|--------|
| Name | Human label |
| Type | See table above |
| Creditor | Descriptive |
| Linked liability account | Exactly one |
| Currency | From account / explicit; no silent FX |
| Priority (emotional) | `high` \| `medium` \| `low` — user choice |
| Status | Lifecycle |
| Notes | Optional empty string allowed; field exists |

### Optional (financial enrichment)

| Field | Notes |
|-------|--------|
| Interest rate (APR) | Many users do not know it |
| Minimum payment | |
| Credit limit | |
| Statement day | Calendar day 1–31 |
| Due / payment day | Calendar day 1–31 |
| Original amount | |
| Maturity date | |
| Opened at | |

Do **not** block creation on missing rates or minimums.

---

## 7. Priority (two concepts)

| Kind | Owner | Purpose |
|------|-------|---------|
| Emotional priority | User | High / medium / low |
| Financial priority | WealthOS (later) | Derived from rate, balance, payment, due date |

Strategies and AI may use financial priority; they never overwrite emotional priority without explicit user action.

---

## 8. Payment strategies (preferences)

Not algorithms that mutate data. User preference only:

- `avalanche`
- `snowball`
- `manual` — “I do not want recommendations”

Strategies **only** produce recommendations. They never change balances, statuses, or transactions by themselves.

---

## 9. What “paying” means

Never mutate Debt to “reduce balance.”

The user records a **transaction** (typically transfer from an asset account into the liability account). The account balance changes; the Debt’s derived balance follows.

There are **no** “manual debt payments” that bypass the ledger.

Payment *links* or audit rows may exist for UX/history, but money movement remains a Transaction.

---

## 10. Net Worth

```text
Assets − Liabilities = Net Worth
```

Debt does **not** change this formula. It adds metadata so liabilities are understandable (who, type, due dates, strategy).

---

## 11. Calendar events (not tasks)

Each debt may generate **financial events**:

- Minimum payment
- Due date
- Statement day
- Estimated payoff

These are calendar signals — not a task system.

---

## 12. Dashboard (consumers)

Relevant, not exhaustive:

- Total liabilities
- Monthly committed payments
- Highest-interest debt
- Closest due date
- Recommended next payment (when strategy ≠ manual)

Future framing:

**Compromisos financieros** — active count, monthly committed outflow, next due, risk band.

---

## 13. Goals / AI (future consumers)

Model must allow questions like: “If I pay the card first, do I reach the house goal sooner?”  
Not implemented in Sprint 6; structure must not block it.

---

## 14. Invariants (never break)

1. A Debt has exactly one liability Account.  
2. Balance never lives on Debt.  
3. Payments are always Transactions.  
4. No ledger-bypassing “manual payments.”  
5. Archive never deletes history.  
6. When the account balance changes, the Debt’s derived reality changes.  
7. Strategies never mutate financial data — only recommendations.  
8. Currency stays explicit; no silent FX.  
9. Organization scoping on every Debt record.

---

## 15. Product naming

| Layer | Name |
|-------|------|
| Backend module | `modules/debts/` |
| Aggregate | Debt |
| UI navigation | **Obligaciones** / Financial Commitments |
| Sprint umbrella | Sprint 6 — Financial Commitments |
| First slice implemented | Debt Management |

Users never need to know the aggregate name.

---

## 16. Acceptance criteria (slice 6.1)

- [x] Single model covers simple and complex obligations  
- [x] Balance provenance documented as Account-only  
- [x] Payments reuse Transactions  
- [x] Dashboard enrichment without duplicated money  
- [x] Strategies / AI possible without structural rewrite  
- [x] Product language + Principle 08 recorded  

Implementation alignment (code ↔ this RFC) continues in **6.2+**.

---

## 17. Convergence notes (existing code)

Prior `modules/debts/` work may require follow-up to match this contract, including:

- Make interest rate and minimum payment **optional**
- Add `creditor`, emotional `priority`, statuses `paused` / `defaulted`
- Expand `debt_type` with `business_loan`, `family_loan`, `installment_plan`
- Auto `paid_off` / revive from account balance
- Persist strategy preference without letting simulators mutate ledger state
- UI copy: Obligaciones (not “Debts”) when frontend lands

Track gaps in Sprint 6.2 SPEC — do not silently keep a second balance field.

---

## Related

- [Sprint 6 — Financial Commitments](../roadmap/sprint-6-financial-commitments.md)
- [Decision: Financial Commitments](../decisions/2026-07-25-financial-commitments.md)
- [PRODUCT_LANGUAGE.md](../product/PRODUCT_LANGUAGE.md)
- [Product Principles](../product/02-product-principles.md)
- [EPIC-005](../epics/EPIC-005-debts.md)
