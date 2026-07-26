# Debts

First **Financial Commitment** type in WealthOS.

## Purpose

Make obligations visible without a second ledger:

```text
Debt → Liability Account → Transactions
```

Product UI: **Obligaciones**. Domain module: `debts/`.

Contract: [RFC-002](../../../../../docs/rfc/RFC-002-financial-commitments.md) · UX: [Sprint 6.2](../../../../../docs/roadmap/sprint-6.2-commitments-ux.md).

## Responsibilities

- Debt aggregate (org-scoped): type, creditor, priority, optional rate/minimums, status
- **Never** store `current_balance` on Debt — derive from liability Account
- Payments only via Transactions
- Archive keeps history; strategies recommend only

## Public API

Under `/api/v1/organizations/{organization_id}` (evolve toward RFC-002):

- `GET/POST /debts`
- `GET/PATCH /debts/{debt_id}`
- Archive / payment endpoints as specified in Sprint 6.2+

## Notes

Sprint: [Financial Commitments](../../../../../docs/roadmap/sprint-6-financial-commitments.md).  
Language: [PRODUCT_LANGUAGE.md](../../../../../docs/product/PRODUCT_LANGUAGE.md).
