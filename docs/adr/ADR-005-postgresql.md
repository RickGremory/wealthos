# ADR-005: PostgreSQL as the system of record

- **Status:** accepted
- **Date:** 2026-07-23
- **Deciders:** WealthOS core

## Context

WealthOS stores financial truth: balances, transactions, goals, tax reserves, and decision history. The primary store must be reliable, transactional, and well-understood for relational modeling and audits.

## Decision

Use **PostgreSQL** as the primary system-of-record database.

## Consequences

### Positive
- Strong ACID transactions for money-related writes
- Mature tooling, backups, extensions, and hosting options
- Fits modular monolith with schema/table ownership per module
- Good fit for reporting and future analytical extracts

### Negative / trade-offs
- Operational ownership (migrations, indexes, vacuum, backups) is mandatory
- Not a replacement for object storage or specialized search — those come later if needed
- Very large analytical workloads may eventually need a warehouse/replica path

## Alternatives considered
- MySQL / MariaDB — viable; PostgreSQL preferred for constraints and ecosystem fit
- MongoDB — flexible documents; weaker fit as sole ledger/system of record
- SQLite only — excellent for local/dev; insufficient as primary cloud SoR at SaaS scale
