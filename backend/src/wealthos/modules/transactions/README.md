# Transactions

Ledger of income, expense, transfer, and adjustment movements with double-entry style entries.

## Public API

Nested under organizations (membership required):

| Method | Path |
|--------|------|
| `POST` | `/api/v1/organizations/{organization_id}/transactions` |
| `GET` | `/api/v1/organizations/{organization_id}/transactions` |
| `GET` | `/api/v1/organizations/{organization_id}/transactions/{transaction_id}` |
| `PATCH` | `/api/v1/organizations/{organization_id}/transactions/{transaction_id}` |
| `POST` | `/api/v1/organizations/{organization_id}/transactions/{transaction_id}/void` |

Roles: viewers read; members create/update metadata; void requires owner/admin.
Amounts and accounts are immutable after posting; void reverses balances.
