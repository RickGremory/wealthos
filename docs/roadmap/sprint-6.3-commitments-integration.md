# Sprint 6.3 — Financial Commitments Integration

**Status:** Accepted  
**Parent:** [Sprint 6 — Financial Commitments](./sprint-6-financial-commitments.md)  
**Depends on:** [RFC-002](../rfc/RFC-002-financial-commitments.md) · [Sprint 6.2 UX](./sprint-6.2-commitments-ux.md)  
**Decision:** [Financial Timeline](../decisions/2026-07-25-financial-timeline.md)

> Integration contract: how Obligaciones enrich the platform **without duplicating money**.  
> Implementation of projections/API lands in **6.4+**; this slice freezes *what* each consumer must see.

---

## Philosophy

A commitment is not an island.

Each WealthOS module answers one question. Commitments answer theirs — and **feed** the others.

| Module | Question |
|--------|----------|
| Accounts | ¿Dónde está mi dinero? |
| Transactions | ¿Qué ocurrió con mi dinero? |
| Dashboard | ¿Cómo está mi salud financiera? |
| Goals | ¿Qué estoy construyendo? |
| **Financial Commitments** | **¿Qué parte de mi futuro ya está comprometida?** |
| Planning | ¿Qué puedo hacer el próximo mes? |
| Taxes | ¿Qué debo reservar al gobierno? |

---

## 1. Dashboard (first consumer)

### Block — Financial Commitments

Answer in &lt; 5 seconds (aligned with 6.2 widget, slightly richer for the home block):

| Signal | Example |
|--------|---------|
| Active commitments | 7 |
| Total committed | $482,500 |
| Monthly payment | $14,350 |
| Next due | HSBC · 3 days |

No full list on the Dashboard.

### Needs Attention

If any commitment is **overdue** (derived UX state), surface it in the existing attention area — user must not open Obligaciones to learn this.

Example: `⚠ HSBC Platinum — Payment overdue by 4 days.`

`needs_attention` is **derived**, never a persisted column.

### Widget states

`loading` · `ready` · `empty` · `restricted` · `error`

Never show a bare `0` / `€0` without empty-state explanation.

### API shape

Do **not** invent a parallel “dashboard debts microservice.” Enrich the org dashboard projection:

```http
GET /organizations/{id}/dashboard
```

```json
{
  "financial_commitments": {
    "active_count": 7,
    "totals_by_currency": [
      { "currency": "MXN", "total_obligations": "482500.00", "monthly_payments": "14350.00" }
    ],
    "next_due": { "commitment_id": "...", "name": "HSBC", "due_in_days": 3 },
    "attention": [
      { "commitment_id": "...", "code": "overdue", "message": "Payment overdue by 4 days." }
    ]
  }
}
```

Dedicated read helpers (e.g. `/dashboard/debts`) may exist for FE composition, but the **canonical home payload** includes `financial_commitments`. Performance: consume **projections**, same pattern as Goals — Dashboard must not recompute heavy payoff math per request from scratch if a projection exists.

---

## 2. Net Worth

Formula unchanged:

```text
Assets − Liabilities = Net Worth
```

Navigation enrichment only:

```text
Net Worth → Liabilities → Financial Commitments → Commitment Detail
```

Dashboard numbers stop being dead ends.

---

## 3. Goals

No extra coupling logic required for progress:

```text
Pay card → liability balance ↓ → Net Worth ↑ → goal progress (if net-worth / linked) improves
```

Automatic via existing sources of truth.

### Prepared copy / ViewModel (do not ship AI yet)

Reserve fields for future guidance, e.g.:

- `This commitment is delaying one of your goals.`
- `Paying this commitment first would improve your monthly cash flow.`

ViewModel hooks only — no recommendation engine in Sprint 6.

---

## 4. Transactions

Commitment detail **reuses** the account’s transaction history.

Filters: Transfers · Charges · Adjustments.

Never duplicate movements into a debt-only ledger.

---

## 5. Calendar

Commitments emit **financial events** (not tasks):

| Event | Source |
|-------|--------|
| Statement date | Optional statement day |
| Payment due date | Due / payment day |
| Estimated payoff | Projection when computable |
| Paused commitment review | Status `paused` |

Appear alongside Goals, Taxes, Recurring, Planning events on the shared calendar surface.

---

## 6. Notifications (future — define only)

Domain-capable events (do not implement delivery yet):

- Payment due tomorrow  
- Minimum payment configured  
- Commitment fully paid  
- New charge detected  

---

## 7. Planning (Sprint 8+)

Cash-flow order becomes realistic:

```text
Income → Fixed expenses → Commitments → Taxes → Safe to Spend
```

---

## 8. Safe to Spend

Today: *How much can I spend?*  
With commitments: *How much can I spend **after** meeting my obligations?*

Concept reserved in [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md); Planning owns the calculation later.

---

## 9. Reports (sections, not a new module)

- Liabilities by Type  
- Monthly Payments  
- Commitments by Creditor  
- Payoff Progress  

---

## 10. Global search

Commitments discoverable like accounts: creditor, type, name (HSBC, Mortgage, Car Loan, Family Loan).

---

## 11. Multi-currency

Never sum across currencies.

Each currency exposes its own Total Obligations and Monthly Payments.

---

## 12. Organizations

Commitments are org-scoped. Never shared across tenants.

---

## 13. Activity moments

When `commitment_paid_off`: celebrate in activity / timeline surfaces, e.g. *HSBC Platinum was fully paid.*

---

## 14. AI foundation (inputs only)

Future strategy inputs (no advice yet): interest rate, balance, monthly payment, income, goals, cash flow, taxes.

---

## 15. Observability events

| Event |
|-------|
| `commitment_created` |
| `commitment_archived` |
| `payment_registered` |
| `commitment_paid_off` |
| `commitment_reopened` |

---

## 16. Financial Timeline (signature concept)

See [decision](../decisions/2026-07-25-financial-timeline.md).

One chronological spine of financial life — not a social feed, not per-module histories. Modules already produce the ingredients (transactions, goals, commitments, calendar, taxes, planning). From now on, prefer **coherent event shapes** so Timeline can assemble later without domain redesign.

Example:

```text
15 Jul  Salary received
18 Jul  Credit card payment
20 Jul  Emergency fund reached 50%
22 Jul  Mortgage payment due tomorrow
25 Jul  Tax estimate updated
```

---

## Acceptance criteria (6.3 design)

- [x] Dashboard enrichment specified without duplicated ledger logic  
- [x] Net Worth drill-down path defined; formula unchanged  
- [x] Goals auto-benefit documented; recommendation ViewModel reserved  
- [x] Transactions reuse mandated  
- [x] Calendar events listed  
- [x] Multi-org + multi-currency rules stated  
- [x] Projection/performance rule aligned with Goals  
- [x] `GET /dashboard` + `financial_commitments` contract sketched  
- [x] Derived attention (not persisted)  
- [x] Financial Timeline reserved as product signature  

---

## Implementation handoff

| Slice | Owns |
|-------|------|
| **6.4** | Domain/API + projections that power `financial_commitments` |
| **6.5** | Strategy preferences (feed future next-action / AI inputs) |
| **6.6** | Dashboard UI block + Needs Attention + Net Worth drill-down |
| **6.7** | Full `/app/commitments` FE per 6.2 |

---

## Related

[PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md) · [RFC-002](../rfc/RFC-002-financial-commitments.md) · [6.2 UX](./sprint-6.2-commitments-ux.md)
