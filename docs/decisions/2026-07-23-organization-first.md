# 2026-07-23 — Organization first

**Type:** Product / tenancy model  
**Status:** Accepted

## Decision

Users never own business data directly. Every business entity belongs to an **Organization**; users are members with roles.

## Why

- Collaboration (accountant, spouse, assistant) without redesign
- Clear multi-tenant SaaS boundary from day one

## Hardened in ADRs

- [ADR-011](../adr/ADR-011-everything-belongs-to-an-organization.md)
- [ADR-012](../adr/ADR-012-organization-is-the-tenant-boundary.md)

This note captures the product “why”; ADRs capture the engineering contract.
