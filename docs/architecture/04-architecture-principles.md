# Architecture Principles

## Modular Monolith

WealthOS starts as a modular monolith.

Modules communicate through well-defined interfaces.

---

## API First

Frontend communicates only through the public API.

---

## Multi-Tenant by Design

Every business entity belongs to an Organization.

Tenant isolation is mandatory.

---

## UUID Everywhere

Public entities use UUID as primary keys.

---

## UTC Everywhere

All timestamps are stored in UTC.

---

## Source of Truth

Transactions represent the financial truth.

Reports are projections derived from transactions.

---

## Stateless Backend

The backend remains stateless.

Authentication is handled using JWT.

---

## Event Ready

Modules may publish domain events even if no event bus exists initially.

This allows future evolution without major refactoring.

---

## AI Ready

Architecture must allow AI services to consume financial context without tight coupling.

---

## Future Friendly

The modular monolith should evolve into independent services only when justified by business growth.
