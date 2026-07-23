# SPEC-001

# Backend Bootstrap

**Status:** Draft (ready for review)  
**Author:** Ricardo Balam  
**Created:** 2026-07-23  
**Parent Epic:** [EPIC-001 Backend Bootstrap](../../epics/EPIC-001-backend-bootstrap.md)  
**Parent RFC:** [RFC-001 Backend Foundation](../../rfc/RFC-001-backend-foundation.md) (**Accepted — do not modify**)  
**Canonical structure:** [backend-structure.md](../../architecture/backend-structure.md)

---

## 1. Objective

Bootstrap the WealthOS backend so that a developer can clone the repo, start services, hit a health endpoint, see Swagger, run tests and lint — with the **domain-oriented modular layout** already in place (empty modules OK).

This SPEC turns RFC-001 into an actionable build plan. It does **not** implement Identity, finance logic, or AI.

---

## 2. Scope

### In scope

- Python project with **uv** (`pyproject.toml`, `uv.lock`)
- Package layout under `src/wealthos/`
- FastAPI app factory + lifespan + root router
- Core: settings, config, logging, database session wiring
- Shared + modules scaffolds (`identity`, `finance`, `goals`, `debts`, `dashboard`, `taxes`, `ai`)
- Docker + Compose (API + PostgreSQL)
- Alembic with empty baseline migration
- Health endpoint `GET /`
- Pytest for health
- Ruff (lint + format)
- GitHub Actions CI (ruff → pytest)
- Pre-commit hooks (ruff, format, tests)
- `backend/README.md` with start commands

### Out of scope

- Auth / JWT usage beyond empty `security.py` stubs
- Organization CRUD or membership APIs
- SQL models for money domains
- Frontend
- Production hardening (beyond sensible defaults)

---

## 3. Folder structure to create

```
backend/
├── pyproject.toml
├── uv.lock
├── README.md
├── Dockerfile
├── src/
│   └── wealthos/
│       ├── __init__.py
│       ├── main.py
│       ├── app/
│       │   ├── __init__.py
│       │   ├── application.py
│       │   ├── lifespan.py
│       │   └── router.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── settings.py
│       │   ├── security.py
│       │   ├── database.py
│       │   ├── logging.py
│       │   ├── exceptions.py
│       │   └── dependencies.py
│       ├── shared/
│       │   ├── __init__.py
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── pagination/
│       │   ├── utils/
│       │   └── events/
│       └── modules/
│           ├── __init__.py
│           ├── identity/          # scaffold only (api/domain/application/infrastructure/schemas/tests)
│           ├── finance/
│           ├── goals/
│           ├── debts/
│           ├── dashboard/
│           ├── taxes/
│           └── ai/
├── tests/
│   ├── __init__.py
│   └── test_health.py
├── alembic/
│   ├── versions/
│   └── env.py                    # as generated / wired to settings
└── scripts/
```

Each module must include at least `__init__.py` and the empty layer folders:

`api/`, `domain/`, `application/`, `infrastructure/`, `schemas/`, `tests/`.

Root repo:

- Update `docker-compose.yml` to run `backend` + `postgres`
- Update `.env.example` with DB and app vars

---

## 4. Dependencies

Managed with **uv**. Pin via lockfile.

### Runtime

| Package | Role |
|---------|------|
| `fastapi` | HTTP API |
| `uvicorn[standard]` | ASGI server |
| `sqlalchemy` | ORM / engine (2.x) |
| `alembic` | Migrations |
| `pydantic` / `pydantic-settings` | Settings & validation |
| `psycopg[binary]` | PostgreSQL driver |

### Dev / quality

| Package | Role |
|---------|------|
| `pytest` | Tests |
| `httpx` | ASGI test client (recommended) |
| `ruff` | Lint + format |
| `pre-commit` | Local hooks |

### Language

- **Python 3.13** (per RFC-001)

---

## 5. uv configuration

- Project name: `wealthos` (or `wealthos-backend` if packaging requires — prefer import package `wealthos`)
- Layout: `src/` layout
- Scripts entry optional: document `uv run uvicorn wealthos.main:app --reload`
- Ruff configured in `pyproject.toml` (`[tool.ruff]`, format enabled)
- Pytest configured (`[tool.pytest.ini_options]`, `pythonpath` / `testpaths = ["tests"]`)

Commands every developer should have:

```bash
cd backend
uv sync
uv run uvicorn wealthos.main:app --reload --host 0.0.0.0 --port 8000
uv run pytest
uv run ruff check .
uv run ruff format .
```

---

## 6. Configuration (`core/`)

### Settings (`settings.py` / `config.py`)

Load from environment (and `.env` in local):

| Variable | Example | Purpose |
|----------|---------|---------|
| `APP_NAME` | `wealthos-api` | Service name in health |
| `APP_VERSION` | `0.1.0` | Version in health |
| `APP_ENV` | `development` | Environment label |
| `DATABASE_URL` | `postgresql+psycopg://…` | SQLAlchemy URL |
| `LOG_LEVEL` | `INFO` | Logging |

Rules:

- No secrets committed
- `.env.example` documents every required key
- Settings object is the single source for runtime config

### Logging (`logging.py`)

- Structured, simple console logging for now
- Configurable level from settings

### Database (`database.py`)

- Engine + session factory
- Dependency for request-scoped session (even if unused by health)
- UTC-aware conventions documented (timestamps later)

### Security (`security.py`)

- Stub only (placeholders for JWT later)
- No auth on health endpoint

### Exceptions / dependencies

- Base app exception type(s)
- Shared FastAPI dependencies hook (empty or session-only)

---

## 7. Docker & PostgreSQL

### `backend/Dockerfile`

- Multi-stage optional; keep simple for bootstrap
- Install via `uv`
- Default CMD: uvicorn on port 8000

### Root `docker-compose.yml`

Services:

- `db` — PostgreSQL 16 (or current stable), volume, healthcheck
- `api` — build `./backend`, depends on healthy `db`, env from `.env`

Developer happy path:

```bash
cp .env.example .env
docker compose up --build
```

---

## 8. Alembic

- Initialized under `backend/alembic/`
- `env.py` reads `DATABASE_URL` from settings
- First revision: **empty** baseline (no tables yet) — proves migration pipeline
- Document:

```bash
uv run alembic upgrade head
uv run alembic revision -m "message"
```

---

## 9. Health API

### Endpoint

`GET /`

### Response — `200 OK`

```json
{
  "service": "wealthos-api",
  "version": "0.1.0",
  "status": "healthy"
}
```

### Requirements

- Registered via `app/router.py`
- Visible in OpenAPI / Swagger (`/docs`)
- No organization context required

Optional later (not this SPEC): `GET /health/ready` with DB ping.

---

## 10. Quality

### Pytest

- `tests/test_health.py` asserts `GET /` → 200 and JSON keys/values
- Prefer FastAPI `TestClient` / `httpx.ASGITransport`

### Ruff

- Lint + format; CI fails on violations
- Align with `.editorconfig` (Python indent 4)

### Pre-commit

On commit (local):

1. `ruff check`
2. `ruff format` (or format-check)
3. `pytest` (or a fast subset if full suite becomes slow — for now full health suite is fine)

### CI (GitHub Actions)

Workflow e.g. `.github/workflows/backend.yml`:

```
ruff → pytest → success
```

Triggers: PR + push to `main` affecting `backend/` (or always until frontend exists).

---

## 11. Tasks checklist

Track progress here. Mark `[x]` as each item lands (commits may group related items).

### WS-1 Bootstrap Project

- [ ] Initialize uv project under `backend/`
- [ ] Create `pyproject.toml` + `uv.lock`
- [ ] Create `src/wealthos/` package layout (app, core, shared, modules scaffolds)
- [ ] Add `backend/README.md`

### WS-2 Configuration

- [ ] Implement settings / config from env
- [ ] Implement logging
- [ ] Wire app factory + lifespan
- [ ] Stub security / exceptions / dependencies

### WS-3 Database

- [ ] SQLAlchemy engine + session
- [ ] Initialize Alembic
- [ ] Empty baseline migration
- [ ] Document migrate commands

### WS-4 Quality

- [ ] Configure Ruff
- [ ] Configure Pytest
- [ ] Add health test
- [ ] Add pre-commit config
- [ ] Add GitHub Actions workflow

### WS-5 Docker

- [ ] `backend/Dockerfile`
- [ ] Root `docker-compose.yml` (api + postgres)
- [ ] Update `.env.example`

### WS-6 Health API

- [ ] Implement `GET /` health payload
- [ ] Confirm Swagger `/docs` loads

---

## 12. Acceptance criteria

SPEC-001 is **Done** when all of the following are true on a clean checkout:

| # | Criterion |
|---|-----------|
| 1 | `uv sync` succeeds in `backend/` |
| 2 | Backend starts (`uv run uvicorn …` **or** `docker compose up`) |
| 3 | Swagger UI available at `/docs` |
| 4 | `GET /` returns **200** with the JSON contract above |
| 5 | Database container is up; app can obtain a SQLAlchemy engine/session (migrate to head succeeds) |
| 6 | `uv run pytest` passes |
| 7 | `uv run ruff check .` passes |
| 8 | CI workflow is present and green on the PR that completes this SPEC |
| 9 | Module scaffolds exist for identity, finance, goals, debts, dashboard, taxes, ai |
| 10 | No domain business logic beyond health / wiring |

---

## 13. Suggested commits

Prefer one theme per commit (matches [CONTRIBUTING](../../../.github/CONTRIBUTING.md)):

| Order | Message |
|-------|---------|
| 1 | `build(backend): initialize Python project with uv` |
| 2 | `build(backend): install project dependencies` |
| 3 | `feat(backend): scaffold domain-oriented module layout` |
| 4 | `feat(backend): add settings, logging, and database config` |
| 5 | `build: add backend Docker setup` |
| 6 | `feat(backend): initialize Alembic with empty migration` |
| 7 | `feat(backend): add health check endpoint` |
| 8 | `test(backend): add health check test` |
| 9 | `ci: add backend lint and test workflow` |
| 10 | `chore: add pre-commit hooks for ruff, format, and tests` |

Commits may be squashed in PR if history gets noisy; the SPEC checklist still tracks completeness.

---

## 14. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Over-building modules | Scaffolds only — empty layers |
| Docker vs local uv drift | Same lockfile; document both paths |
| Python 3.13 image availability | Pin image tag; fallback 3.12 only via ADR/SPEC amendment |
| Pre-commit too slow | Allow `SKIP` for emergencies; keep CI as source of truth |

---

## 15. Approval

| Role | Name | Decision |
|------|------|----------|
| Author | Ricardo Balam | Draft |
| Reviewer | — | Pending |

**Next step after approval:** implement WS-1 (no code before this SPEC is Accepted).

When approved, change **Status** at the top to `Accepted` and start coding against the checklist.
