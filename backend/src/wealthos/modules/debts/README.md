# Debts

## Purpose

Track **liabilities** so net worth is honest:

```text
Assets − Liabilities = Net Worth
```

Debts never invent a second ledger: balances and payments must remain explainable against financial accounts and transactions.

## Responsibilities

- Debt aggregate (org-scoped): type, balance, currency, rate, minimums, status
- Archive / restore (mistake recovery) rather than silent hard delete
- Feed Dashboard liabilities and (later) Planning / Goals / AI consumers

## Public API

Target (Sprint 6 — see [sprint brief](../../../../../docs/roadmap/sprint-6-debt-management.md)):

- `GET/POST /organizations/{organization_id}/debts`
- `GET/PATCH /organizations/{organization_id}/debts/{debt_id}`
- Archive (and optional restore) endpoints

## Notes

Scaffold exists; feature work starts in Sprint 6 ([EPIC-005](../../../../../docs/epics/EPIC-005-debts.md)).
Register in `wealthos.modules.MODULES` when HTTP routes ship.
