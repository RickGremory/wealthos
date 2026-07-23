# ADR-011

# Everything Belongs to an Organization

**Status:** Accepted

**Date:** 2026-07-23

---

## Context

WealthOS is designed as a multi-tenant SaaS from day one.

Many personal finance applications associate data directly with a user. While this approach is simple, it becomes limiting when supporting accountants, assistants, spouses, business partners or teams.

The system should support collaboration without redesigning the data model in the future.

---

## Decision

Every business entity belongs to an Organization.

Users never own business data directly.

Instead, users are members of one or more organizations with specific roles and permissions.

---

## Example

```
Organization
├── Ricardo (Owner)
├── Accountant (Accountant)
├── Assistant (Editor)
└── Gaspar (Viewer)
        ↓
    Accounts
        ↓
    Transactions
        ↓
    Goals
        ↓
    Debts
        ↓
    Tax Profiles
```

---

## Benefits

- Native multi-tenancy.
- Easier collaboration.
- Better permission model.
- Future support for companies and families.
- Cleaner ownership model.

---

## Consequences

Every domain entity must include an organization reference.

Authorization will always be evaluated within an organization context.

---

## Alternatives Considered

### User as Tenant

Rejected.

Does not scale well to collaborative scenarios.

### Workspace Model

Considered.

An Organization already fulfills this responsibility with clearer terminology.

---

## Status

Accepted.
