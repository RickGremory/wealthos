# ADR-004: Modular monolith architecture

- **Status:** accepted
- **Date:** 2026-07-23
- **Deciders:** WealthOS core

## Context

Early-stage WealthOS must move fast while keeping financial domains (accounts, cashflow, taxes, goals, debt) coherent. Premature microservices would multiply ops cost before product-market fit.

## Decision

Build WealthOS backend as a **modular monolith**:

- One deployable backend application
- Internal modules / bounded contexts with explicit boundaries
- Shared database allowed initially, with clear ownership of tables/schemas per module
- Extract services later only when scale, team, or isolation demands it

## Consequences

### Positive
- Single deploy and simpler local development
- Transactions and consistency are easier across related domains
- Modules can still enforce boundaries in code and packages

### Negative / trade-offs
- Discipline required to avoid a “ball of mud”
- Scaling is vertical / app-level first; not independently scalable per domain
- Future extraction needs clear module interfaces from day one

## Alternatives considered
- Microservices from day one — isolation at high ops cost; rejected for now
- Classic unstructured monolith — fastest short term; costly long term
- Modular monorepo with many independently deployed services — deferred
