# Organizations

Reference domain module for WealthOS.

## Purpose

An **Organization** is the financial workspace where money lives — not a user,
not a company label alone, and not a technical tenant table by itself.

Examples: `Ricardo Personal`, `Tecnicora`, `Consultoría USA`.

Everything else (accounts, transactions, goals, debts, taxes, AI context)
belongs to an Organization.

## Domain model

- Rich entity: `Organization` with domain `UUID` identity
- Value objects: `OrganizationName`, `OrganizationSlug`, `Currency`, `Timezone`, `Locale`
- Port: `OrganizationRepository` (`add`, `get_by_id`, `get_by_slug`)

## Create flow (reference path)

```
POST /api/v1/organizations
  → OrganizationCreate
  → CreateOrganizationCommand
  → Organization.create(...)
  → OrganizationRepository.add
  → Mapper / Model / PostgreSQL
  → Organization
  → OrganizationResponse
```

## Public API

| Method | Path | Status |
|--------|------|--------|
| `GET` | `/api/v1/organizations/health` | scaffold probe |
| `POST` | `/api/v1/organizations` | create workspace (`201`) |
| `POST` | `/api/v1/organizations/{id}/members` | add member (`201`) |
| `GET` | `/api/v1/organizations/{id}/members` | list members |

Defaults: `currency=MXN`, `timezone=America/Cancun`, `locale=es-MX`.

Memberships link users (identity module) to organizations. Owner auto-assignment
on create waits for authentication.

## How to extend

Follow `docs/engineering/CODING_STANDARDS.md` and copy this module’s patterns.
