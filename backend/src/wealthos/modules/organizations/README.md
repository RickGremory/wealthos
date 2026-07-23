# Organizations

Reference domain module for WealthOS.

## Purpose

An **Organization** is the financial workspace where money lives — not a user,
not a company label alone, and not a technical tenant table by itself.

Examples: `Ricardo Personal`, `Tecnicora`, `Consultoría USA`.

Everything else (accounts, transactions, goals, debts, taxes, AI context)
belongs to an Organization.

## Domain model

- Rich entity: `Organization` (no technical `id` in the domain)
- Value objects: `Name`, `Slug`, `Currency`, `Timezone`, `Locale`
- Port: `OrganizationRepository` → returns `OrganizationSnapshot` after write
- Persistence identity (UUID + timestamps) lives in infrastructure

## Create flow (reference path)

```
POST /organizations
  → OrganizationCreate (schema)
  → CreateOrganizationCommand
  → Organization.create(...)
  → OrganizationRepository.add
  → OrganizationMapper / OrganizationModel
  → Database
  → OrganizationSnapshot
  → OrganizationRead
```

## Public API

| Method | Path | Status |
|--------|------|--------|
| `GET` | `/organizations/health` | scaffold probe |
| `POST` | `/organizations` | create workspace |

## How to extend

Follow `docs/engineering/CODING_STANDARDS.md` and copy this module’s patterns.
