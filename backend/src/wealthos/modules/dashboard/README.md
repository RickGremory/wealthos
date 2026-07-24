# Dashboard

Read-only financial overview for an organization.

## Semantics

- **Balances / net worth**: current account state (not period-dependent).
- **Cash flow**: posted income and expense in the selected period only.
- **Transfers / adjustments**: excluded from income, expenses, and net cash flow.
- **Voided transactions**: excluded from cash-flow metrics.
- **Multi-currency**: amounts are grouped by currency; no FX conversion.
- **Expenses / liabilities**: returned as positive display values.
- **date_to**: inclusive for consumers; stored queries use a half-open UTC interval.

## Public API

| Method | Path |
|--------|------|
| `GET` | `/api/v1/organizations/{organization_id}/dashboard/summary` |
| `GET` | `/api/v1/organizations/{organization_id}/dashboard/cash-flow` |
| `GET` | `/api/v1/organizations/{organization_id}/dashboard/spending-by-category` |
| `GET` | `/api/v1/organizations/{organization_id}/dashboard/accounts` |
| `GET` | `/api/v1/organizations/{organization_id}/dashboard/recent-transactions` |
