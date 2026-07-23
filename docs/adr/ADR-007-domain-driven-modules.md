# ADR-007: Domain-driven modules

- **Status:** accepted
- **Date:** 2026-07-23
- **Deciders:** WealthOS core

## Context

WealthOS is a modular monolith ([ADR-004](./ADR-004-modular-monolith.md)) with clear domain invariants (transactions as source of truth, Organization ownership, goals never own money). Without intentional module boundaries, FastAPI routes and models tend to collapse into a single tangled package.

## Decision

Organize backend code as **domain-driven modules** (bounded contexts) inside the monolith:

- Each module owns its domain language, application services, and persistence mapping for that context
- Cross-module collaboration goes through explicit interfaces / application APIs — not reaching into another module’s internals
- Shared kernels stay thin (`UUID`, UTC helpers, Organization id types) — not a dumping ground for business rules
- Modules align to product domains (e.g. identity/orgs, ledger/transactions, goals, taxes, debt) as they are introduced

## Consequences

### Positive
- Keeps financial domains coherent as the codebase grows
- Makes future extraction possible without a rewrite
- Clarifies ownership for reviews and testing

### Negative / trade-offs
- Requires discipline and occasional “where does this belong?” decisions
- Early modules may be thin until product surface expands
- Shared DB still needs table/schema ownership conventions

## Alternatives considered
- **Layer-only structure** (`models/`, `services/`, `api/`) — simple; becomes a ball of mud at scale
- **Microservices per domain** — premature for current stage ([ADR-004](./ADR-004-modular-monolith.md))
- **Package-by-technical-concern only** — rejects domain language as the primary seam
