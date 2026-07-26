# Debts

First **Financial Commitment** type in WealthOS.

## Purpose

Make obligations visible without a second ledger:

```text
Debt → Liability Account → Transactions
```

Product UI: **Obligaciones**. Domain module: `debts/`.

Contract: [RFC-002](../../../../../docs/rfc/RFC-002-financial-commitments.md) · [SPEC-002](../../../../../specs/backend/debts/SPEC-002-financial-commitments.md).

## Phase 1 (done)

- Persisted status: `active` | `paused` | `defaulted` | `closed` | `archived` (no stored `paid_off`)
- Derived display status via `DebtStateService` (`settled`, `overdue`, `paid_off`, …)
- `UNIQUE(account_id)` · interest as percent `Numeric(9,6)` (`42.5` → `42.500000`)
- Optional rate / minimum / scheduled payment · creditor · priority · `version`
- Due day 31 → last day of month

## Responsibilities

- Debt aggregate (org-scoped): metadata only — **never** store `current_balance`
- Payments via transactions / transfers (Phase 5+); archive keeps history
- Strategies recommend only (Phase 3+)

## Public API (current + evolving)

Under `/api/v1/organizations/{organization_id}`:

- `GET/POST /debts` (canonical path becomes `/commitments` in later phases)
- Lifecycle: archive; pause/resume/close land in Phase 2

## Notes

Interest rate convention: **percent**, six decimal places — never store `0.425` for 42.5%.
