# ADR-001: FastAPI for the backend

- **Status:** accepted
- **Date:** 2026-07-23
- **Deciders:** WealthOS core

## Context

WealthOS needs a backend API for domain logic, auth, and integrations. The stack should favor clear contracts, fast iteration, and strong typing without heavy ceremony.

## Decision

Use **FastAPI** (Python) as the primary backend framework for HTTP APIs.

## Consequences

### Positive
- Native OpenAPI / typed request-response models
- Async-friendly for I/O-bound workloads
- Large ecosystem for data, auth, and tooling

### Negative / trade-offs
- Python ops and packaging discipline required
- CPU-heavy workloads may need separate workers later
- Team must keep domain logic out of route handlers

## Alternatives considered
- NestJS / Node — strong for TS monorepos; rejected for now to keep backend domain in Python
- Django — richer batteries; heavier for a focused API-first open-core product
- Go (stdlib / Fiber) — excellent performance; slower product iteration for this stage
