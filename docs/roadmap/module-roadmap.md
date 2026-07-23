# Module Roadmap

Order in which WealthOS domain capabilities are introduced.

This is a **delivery sequence**, not a dependency-free list: later modules assume earlier ones exist.

**Related:** [backend-structure.md](../architecture/backend-structure.md), [Sprint 1](./sprint-1-backend-foundation.md), [ADR-007](../adr/ADR-007-domain-driven-modules.md), [ADR-008](../adr/ADR-008-dashboard-as-product-center.md), [ADR-011](../adr/ADR-011-everything-belongs-to-an-organization.md).

---

## Sequence

```
Identity
  ↓
Organizations
  ↓
Accounts
  ↓
Transactions
  ↓
Categories
  ↓
Dashboard
  ↓
Goals
  ↓
Debts
  ↓
Taxes
  ↓
AI
```

---

## Why this order

| Step | Module / capability | Why here |
|------|---------------------|----------|
| 1 | **Identity** | Auth and users before any tenant data |
| 2 | **Organizations** | Multi-tenant root: everything belongs to an Organization |
| 3 | **Accounts** | Places where money lives (wallets, banks, cash) |
| 4 | **Transactions** | Source of truth for financial reality |
| 5 | **Categories** | Structure spending/income without rewriting the ledger |
| 6 | **Dashboard** | Product center — answers questions from projections |
| 7 | **Goals** | Targets that never own money; progress from transactions/accounts |
| 8 | **Debts** | Obligations visible against the same financial reality |
| 9 | **Taxes** | Reserves/estimates grounded in income transactions |
| 10 | **AI** | Consumes structured context only after the ledger is trustworthy |

---

## Mapping to `modules/`

| Roadmap step | Package under `src/wealthos/modules/` | Notes |
|--------------|----------------------------------------|--------|
| Identity | `identity/` | Users, credentials/session, membership hooks |
| Organizations | `identity/` (or split later) | Org entity + tenant isolation; may start inside `identity/` |
| Accounts | `finance/` | Account aggregate |
| Transactions | `finance/` | Ledger entries — source of truth |
| Categories | `finance/` | Classification of transactions |
| Dashboard | `dashboard/` | Read models / answers for the home experience |
| Goals | `goals/` | Goals never hold balances |
| Debts | `debts/` | Debt tracking |
| Taxes | `taxes/` | Tax reserve / estimates |
| AI | `ai/` | Context APIs / coaching seams — not a second ledger |

`finance/` therefore lands in slices: **Accounts → Transactions → Categories**, not as one big bang.

---

## Invariants (every step)

- UUID primary keys
- UTC timestamps
- Organization scoping on every domain record
- Transactions remain the source of truth
- Goals never own money
- Dashboard numbers must be explainable back to transactions

---

## Delivery guidance

1. **Do not skip** Identity / Organizations before money modules.
2. **Do not build Dashboard widgets** on mock data that cannot later bind to transactions.
3. **Do not start AI** until Accounts + Transactions (+ Categories) produce a coherent picture.
4. Goals, Debts, and Taxes may share UI space with the Dashboard, but their **domain modules** still follow this order.

---

## Status vs Sprint 1

Sprint 1 scaffolds empty module folders and platform plumbing.

This roadmap governs **feature order after the foundation** (and may overlap early identity/org work once Sprint 1 health/CI is green).

---

## Status

Accepted as the product/module delivery order for WealthOS core.
