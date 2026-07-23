# ADR-001

# Choose FastAPI as Backend Framework

**Status:** Accepted

**Date:** 2026-07-23

---

## Context

WealthOS requires a backend capable of supporting a modern SaaS architecture while remaining easy to maintain and ready for future AI integrations.

Although the founder has significant experience with Laravel and Odoo, the project is intended to be both a production application and a learning opportunity.

---

## Decision

Use FastAPI as the backend framework.

---

## Alternatives Considered

- Laravel
- Django
- Flask
- NestJS

---

## Why FastAPI

- Excellent typing support
- Modern Python ecosystem
- Native OpenAPI generation
- High performance
- Great developer experience
- Excellent compatibility with AI tooling

---

## Consequences

### Positive

- Better long-term alignment with AI features.
- Strong typing.
- Automatic API documentation.

### Negative

- Learning curve.
- Smaller ecosystem than Laravel.

---

## Review

This decision should be revisited only if FastAPI no longer satisfies product requirements.
