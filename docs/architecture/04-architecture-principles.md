# Architecture Principles

Constraints that keep the system coherent as it grows.

## 1. Bounded contexts over a blob
Separate domains (accounts, transactions, goals, identity, etc.) with clear ownership.

## 2. Domain in the backend
Business rules live server-side. UI reflects state; it does not invent financial truth.

## 3. Durable records
Prefer append-friendly history for money events and decisions over silent overwrite.

## 4. Environment isolation
Dev / staging / prod stay distinct. Infrastructure as code lives in `infrastructure/`.

## 5. Dependency direction
Inner domain does not depend on outer delivery details (HTTP frameworks, UI kits, vendors).

## 6. Fail safe with money
When unsure, refuse or quarantine rather than guess a balance or transfer.

## 7. Document the hard calls
Architecture decisions go in `docs/decisions/05-decision-log.md` (and deeper ADRs in `docs/adr/`).

## Status
Draft. See also `.ai/architecture.md` for agent-oriented notes.
