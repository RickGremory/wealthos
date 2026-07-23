# Backend Structure

Canonical layout for the WealthOS FastAPI modular monolith.

**Related:** [ADR-004](../adr/ADR-004-modular-monolith.md), [ADR-007](../adr/ADR-007-domain-driven-modules.md), [Sprint 1](../roadmap/sprint-1-backend-foundation.md), [SPEC-001](../../specs/backend/bootstrap/SPEC-001-backend-bootstrap.md).

---

## Design intent

- Organize by **business domains**, not global technical layers.
- Keep each module **self-contained** so it can become a service later if justified.
- Share only thin primitives via `core/` and `shared/`.
- Package root: `wealthos` under `src/` (import path: `wealthos...`).

---

## Repository tree (`backend/`)

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

---

## Top-level packages

| Path | Responsibility |
|------|----------------|
| `wealthos/main.py` | Process entrypoint (Uvicorn target) |
| `wealthos/app/` | Compose the FastAPI app: factory, lifespan, root router |
| `wealthos/core/` | Cross-cutting runtime: settings, DB, security, logging, shared deps |
| `wealthos/shared/` | Reusable helpers that are not domain logic (pagination, shared schemas, event types) |
| `wealthos/modules/` | Bounded contexts — one folder per business capability |
| `tests/` | Cross-module / app-level tests (health, wiring) |
| `alembic/` | Migrations |
| `scripts/` | Dev/ops helpers |

### Avoid at repository / package root

```
controllers/
models/
services/
repositories/
```

Those names may exist **inside** a module’s `infrastructure/` or `application/`, never as the global organizing principle.

---

## Module template (identical for every domain)

Example: `finance/`

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

### Layer roles

| Layer | Owns | Must not own |
|-------|------|----------------|
| `api/` | HTTP routes, request deps, HTTP response shaping | Business rules, SQL |
| `domain/` | Entities, value objects, domain events/exceptions | Frameworks, DB, FastAPI |
| `application/` | Use cases: commands, queries, application services, DTOs | HTTP details, ORM models |
| `infrastructure/` | SQLAlchemy models, repositories, mappers to/from domain | Product policy / domain invariants |
| `schemas/` | Pydantic API schemas (if kept separate from `api/`) | Domain entities |
| `tests/` | Module-scoped unit/integration tests | — |

### Dependency direction

```
api → application → domain
         ↓
   infrastructure → domain
```

- Outer layers depend inward.
- `domain/` depends on nothing in FastAPI/SQLAlchemy.
- Other modules talk through **application APIs / events**, not by importing another module’s `infrastructure/`.

---

## Planned modules

| Module | Purpose (initial) |
|--------|-------------------|
| `identity/` | Users, auth, Organization membership |
| `finance/` | Accounts, transactions, categories (source of truth) |
| `goals/` | Goals as targets (never own money) |
| `debts/` | Debt tracking |
| `taxes/` | Tax reserve / estimates |
| `dashboard/` | Product center projections and answers |
| `ai/` | AI-ready context consumers / future coaching seams |

**Delivery order:** [module-roadmap.md](../roadmap/module-roadmap.md)

Empty module scaffolds in Sprint 1 are OK — structure before features.

---

## `app/` composition

- `application.py` — create and configure the FastAPI instance
- `lifespan.py` — startup/shutdown (DB, logging hooks)
- `router.py` — mount module routers + health

`main.py` should stay thin: call the app factory.

---

## Why this shape

1. **Domain clarity** — finance language lives in `finance/`, not in a global `services/` dump.
2. **Testability** — domain and application can be tested without HTTP.
3. **Extraction path** — a mature module can move out with its `api/domain/application/infrastructure` intact.
4. **AI-ready** — structured context can be assembled from application/query layers without scraping controllers.
5. **Dashboard-first product** — `dashboard/` consumes projections; it does not become a second ledger.

---

## Status

Documented target for Sprint 1.3+. Implementation lands incrementally; do not invent parallel layouts.
