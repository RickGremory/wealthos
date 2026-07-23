# RFC-001

# Backend Foundation

**Author:** Ricardo Balam

**Status:** Accepted

**Created:** 2026-07-23

> **Frozen.** This RFC is the technical contract for Backend Foundation.  
> Do not expand it with implementation checklists.  
> Execution continues via [EPIC-001](../epics/EPIC-001-backend-bootstrap.md) and [SPEC-001](../specs/backend/bootstrap/SPEC-001-backend-bootstrap.md).  
> See [Delivery Workflow](../engineering/11-delivery-workflow.md).

---

# Summary

Define the foundational architecture of the WealthOS backend.

This RFC establishes the project structure, modular boundaries, engineering conventions and development principles that every future module must follow.

---

# Motivation

A solid backend foundation reduces future refactoring and provides consistency across the entire codebase.

The backend should prioritize:

- Simplicity
- Maintainability
- Testability
- AI-readiness
- Modularity

---

# Goals

The backend must provide:

- Modular architecture
- Domain-oriented structure
- Strong typing
- Automatic API documentation
- Dependency injection
- Configuration management
- Database migrations
- Testing infrastructure
- Docker-based services

---

# Non Goals

This RFC does not define:

- Authentication
- Business rules
- Financial calculations
- AI implementation

---

# Architecture

The backend follows a Modular Monolith architecture.

Each module owns:

- API
- Domain
- Application
- Infrastructure

Modules communicate through public interfaces.

See also: [ADR-004](../adr/ADR-004-modular-monolith.md), [ADR-007](../adr/ADR-007-domain-driven-modules.md), [backend-structure.md](../architecture/backend-structure.md).

---

# Project Structure

```
backend/
│
├── pyproject.toml
├── uv.lock
├── README.md
│
├── src/
│   └── wealthos/
│       │
│       ├── app/
│       │   ├── application.py
│       │   ├── lifespan.py
│       │   └── router.py
│       │
│       ├── core/
│       │   ├── config.py
│       │   ├── settings.py
│       │   ├── security.py
│       │   ├── database.py
│       │   ├── logging.py
│       │   ├── exceptions.py
│       │   └── dependencies.py
│       │
│       ├── shared/
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── pagination/
│       │   ├── utils/
│       │   └── events/
│       │
│       ├── modules/
│       │   ├── identity/
│       │   ├── finance/
│       │   ├── goals/
│       │   ├── debts/
│       │   ├── dashboard/
│       │   ├── taxes/
│       │   └── ai/
│       │
│       └── main.py
│
├── tests/
│
├── alembic/
│
└── scripts/
```

Avoid global `controllers/`, `models/`, `services/`, `repositories/` at the package root.

---

# Module Structure

Every module follows exactly this structure (example: `finance/`):

```
finance/
├── api/
│   ├── router.py
│   ├── dependencies.py
│   └── responses.py
│
├── domain/
│   ├── entities.py
│   ├── value_objects.py
│   ├── events.py
│   └── exceptions.py
│
├── application/
│   ├── services.py
│   ├── commands.py
│   ├── queries.py
│   └── dto.py
│
├── infrastructure/
│   ├── models.py
│   ├── repository.py
│   └── mapper.py
│
├── schemas/
│
├── tests/
│
└── __init__.py
```

Dependency direction: `api → application → domain`; `infrastructure → domain`.

---

# Design Principles

- Domain First
- API First
- Explicit Dependencies
- Composition over Inheritance
- Small Services
- Testability

---

# Technology Stack

## Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic v2
- uv

## Infrastructure

- PostgreSQL
- Docker
- Docker Compose

## Quality

- Ruff
- Pytest
- pre-commit

---

# Risks

Potential learning curve due to Python ecosystem.

**Mitigation:** Incremental implementation with strong documentation.

---

# Success Criteria

The backend can be started with a single command.

Every module follows the same architecture.

Developers can create new modules without modifying the existing architecture.

---

# References

- [Sprint 1 — Backend Foundation](../roadmap/sprint-1-backend-foundation.md)
- [Backend Structure](../architecture/backend-structure.md)
- [ADR-001 FastAPI](../adr/ADR-001-fastapi.md)
- [ADR-005 PostgreSQL](../adr/ADR-005-postgresql.md)
- [ADR-006 uv](../adr/ADR-006-uv-package-manager.md)
