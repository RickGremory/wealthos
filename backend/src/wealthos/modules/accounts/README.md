# Accounts

Financial containers (bank, cash, credit, investment, etc.) belonging to an Organization.

## Public API

Nested under organizations (membership required):

| Method | Path |
|--------|------|
| `POST` | `/api/v1/organizations/{organization_id}/accounts` |
| `GET` | `/api/v1/organizations/{organization_id}/accounts` |
| `GET` | `/api/v1/organizations/{organization_id}/accounts/{account_id}` |
| `PATCH` | `/api/v1/organizations/{organization_id}/accounts/{account_id}` |
| `POST` | `/api/v1/organizations/{organization_id}/accounts/{account_id}/archive` |

Roles: viewers read; members/admins/owners write; archive requires owner/admin.
