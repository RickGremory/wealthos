# Organizations

Reference domain module for WealthOS.

## Purpose

An **Organization** is the financial workspace where money lives — not a user,
not a company label alone, and not a technical tenant table by itself.

Examples: `Ricardo Personal`, `Tecnicora`, `Consultoría USA`.

Everything else (accounts, transactions, goals, debts, taxes, AI context)
belongs to an Organization.

## Domain model (Sprint 2.1)

- Rich entity: `Organization`
- Value objects: `Name`, `Slug`, `Currency`, `Timezone`, `Locale`
- Port: `OrganizationRepository` (Protocol — no SQLAlchemy)
- Persistence identity (UUID/ULID/…) is an **infrastructure** concern

## Public API

- Scaffold: `GET /organizations/health`
- Next sprint: `POST /organizations` (create) and remaining CRUD

## How to extend

Follow `docs/engineering/CODING_STANDARDS.md` and copy this module’s patterns.
