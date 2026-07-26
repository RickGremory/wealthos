# Sprint 6.2 — Financial Commitments UX & User Flows

**Status:** Accepted  
**Parent:** [Sprint 6 — Financial Commitments](./sprint-6-financial-commitments.md)  
**Domain contract:** [RFC-002](../rfc/RFC-002-financial-commitments.md)  
**Decision:** [Next Action pattern](../decisions/2026-07-25-commitments-ux-next-action.md)

> Design contract only. No Vue screens are required to close 6.2.  
> Implementation follows in **6.3+** (API) and **6.6** (frontend).

---

## Philosophy

> Debts create stress; the interface must not.

Show orientation before lists. Cards over tables. One clear next step before raw metrics.

---

## 1. Navigation

Top-level item — **not** nested under Accounts.

```text
Dashboard
Accounts
Transactions
Goals
────────────
Financial Commitments    ← /app/commitments
────────────
Planning
Calendar
Settings
```

Same order on mobile. Concept is distinct from “where money lives.”

| Locale | Nav label |
|--------|-----------|
| EN | Financial Commitments |
| ES | Obligaciones |

Target route prefix: **`/app/commitments`** (not `/app/debts`).

---

## 2. Index — panorama first

**Route:** `/app/commitments`

Not a table. Start with context.

### Header

- Title: **Financial Commitments**
- Subtitle: *Understand what your future income is already committed to.*
- Primary CTA: **+ New Commitment**

### Summary strip (four cards only)

| Card | Example |
|------|---------|
| Total Obligations | $482,500 |
| Monthly Payments | $14,350 |
| Active Commitments | 6 |
| Next Due | HSBC · 3 days |

No extra vanity metrics.

### Main list — cards, never tables

Each card is fully clickable (`role` appropriate for a link/button to detail). Example fields:

- Icon + name + type (and/or creditor)
- Balance (derived from liability account)
- Minimum or monthly payment (if known)
- Due / next payment date
- Status badge
- Optional footer affordance: View Details (whole card still navigates)

Works stacked on mobile; never horizontal scroll tables.

---

## 3. Visual status badges

| Badge | Color intent |
|-------|----------------|
| Active | Neutral / brand |
| Paid Off | Positive / calm |
| Paused | Muted |
| Overdue | **Only** state that uses strong danger (red) |

**Overdue** is a **derived UX state** (due date passed + still owes), not necessarily a persisted domain status. Domain statuses remain per RFC-002 (`active`, `paid_off`, `paused`, `defaulted`, `archived`).

---

## 4. Default sort (never alphabetical)

1. Overdue  
2. Due soon  
3. Highest balance  
4. Everything else  

---

## 5. Create flow

### Step A — type first (no form yet)

**What kind of commitment?**

- Credit Card  
- Mortgage  
- Vehicle Loan  
- Personal Loan  
- Business Loan  
- Student Loan  
- Installments (MSI)  
- Other  

### Step B — form

**Required**

- Name  
- Creditor  
- Currency  
- Linked Liability Account  

**Optional**

- Interest Rate  
- Minimum Payment  
- Due Day  
- Credit Limit  
- Notes  

(Priority may be set with a sensible default, e.g. Medium — align with RFC required emotional priority.)

### Liability account picker

- Only **liability** accounts.  
- If none: *You don't have any liability accounts yet.* + **[Create Liability Account]** without leaving the commitment flow.

---

## 6. Detail

**Route:** `/app/commitments/{id}`

### Header

- Name  
- Balance (derived)  
- Type · Creditor · Priority  

### Fixed section — **What should I do next?**

Always first below the header. One sentence. Examples:

| Situation | Next action copy |
|-----------|------------------|
| Card with minimum + due | Pay at least $1,250 before 25 Jul to avoid late fees. |
| Mortgage with schedule | Your next payment is due on 12 Aug. |
| Family loan, no schedule | No payment schedule configured yet. |
| Paid off | This commitment is paid off. You can archive it anytime. |

This pattern is reusable later on Goals, Taxes, Planning, and Dashboard.

### Info cards (only what’s useful)

1. Current Balance  
2. Minimum Payment  
3. Interest Rate  
4. Next Due Date  
5. Estimated Payoff (if computable)

### History — reuse Transactions

Filter/show movements of the linked liability account:

- Payments  
- Charges  
- Adjustments  

No parallel payment history store.

### Payment CTA (domain-aligned)

There is **no** “Make Payment” that invents a second payment engine.

Primary action opens **New Transfer** with the liability account **preselected** (asset → liability).

UI label may read **New Payment** as shorthand; the underlying flow is Transfer / Transaction.

### Quick actions

- New Payment (→ transfer flow)  
- Edit  
- Pause  
- Archive  

---

## 7. Empty state

> You don't have any financial commitments.  
> Add your first credit card, loan or mortgage.

**[Create Commitment]**

Suggest chips/examples: Credit Card · Mortgage · Car Loan.

---

## 8. Paid off state

Do **not** hide. Celebrate calmly:

> Paid Off — Congratulations! This commitment has been fully paid.

User may archive afterward.

---

## 9. Responsive & a11y

- Mobile: stacked cards only.  
- Entire card activates navigation (not only a text link).  
- Keyboard focus and accessible name required on cards.

---

## 10. Dashboard widget (commitments)

Only three signals:

1. Total Obligations  
2. Monthly Payments  
3. Next Due  

Nothing else in v1 of this widget.

---

## 11. Screen states

Every commitments screen must support:

`loading` · `empty` · `ready` · `error` · `archived` · `restricted`

---

## 12. Search & filters

**Search:** name, creditor, type (e.g. HSBC, BBVA, Mortgage).

**Filters (only):** Status · Type · Currency · Priority.

**Bulk actions:** none in Sprint 6.

---

## 13. Motion budget

Only three intentional animations:

1. Create  
2. Archive  
3. Mark / reveal paid off  

No decorative motion beyond that.

---

## 14. Acceptance criteria (6.2 design)

- [x] User can grasp obligation health in &lt; 10 seconds (panorama + four summary cards + next due)  
- [x] Create flow: type → form → liability-only account (inline create if missing)  
- [x] Payments reuse Transfers/Transactions — no parallel payment engine  
- [x] Card-first layout specified for mobile and desktop  
- [x] No duplicated financial truth (balances/history from accounts/transactions)  
- [x] Cards show decision-useful fields only  
- [x] **What should I do next?** mandated on detail (and reusable product pattern)  

---

## Implementation handoff

| Slice | Owns |
|-------|------|
| 6.3 | Ecosystem integration contract |
| 6.4 | API/domain fields + projections the UX and Dashboard need |
| 6.5 | Strategy preferences (feeds future next-action copy) |
| 6.6 | Dashboard UI block + Needs Attention + Net Worth drill-down |
| 6.7 | Nuxt routes `/app/commitments`, nav label, cards, flows |

---

## Related

- [PRODUCT_LANGUAGE — Next Action](../product/PRODUCT_LANGUAGE.md)  
- [RFC-002](../rfc/RFC-002-financial-commitments.md)
