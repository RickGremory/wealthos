# SPEC-001

# Backend Bootstrap

| Field | Value |
|-------|-------|
| **Status** | Draft (ready for review) |
| **Author** | Ricardo Balam |
| **Created** | 2026-07-23 |
| **Parent Epic** | [EPIC-001](../../docs/epics/EPIC-001-backend-bootstrap.md) |
| **Parent RFC** | [RFC-001](../../docs/rfc/RFC-001-backend-foundation.md) (Accepted — frozen) |
| **Structure** | [backend-structure.md](../../docs/architecture/backend-structure.md) |

> Once **Completed**, this SPEC is immutable. Further changes require a new SPEC.

---

## 1. Objective

Bootstrap the WealthOS backend so a developer can clone the repo, start the API (locally or via Docker), open Swagger, hit a health endpoint, run tests and lint — with the domain-oriented modular layout already scaffolded.

This is the execution contract for the first backend sprint. It implements RFC-001 as code structure and tooling, not as domain features.

---

## 2. Scope

- Initialize Python project with **uv** (`pyproject.toml`, `uv.lock`)
- Create package layout under `src/wealthos/`
- Wire FastAPI app factory, lifespan, and root router
- Core: settings, config, logging, database session
- Scaffold `shared/` and modules: identity, finance, goals, debts, dashboard, taxes, ai
- Docker + Compose (API + PostgreSQL)
- Alembic with empty baseline migration
- Health endpoint `GET /`
- Pytest for health
- Ruff (lint + format)
- GitHub Actions CI (`ruff` → `pytest`)
- Pre-commit (ruff, format, tests)
- `backend/README.md` with start commands
- Update root `.env.example` and `docker-compose.yml`

---

## 3. Out of Scope

- Authentication / JWT flows (beyond empty `security.py` stubs)
- Organization CRUD or membership APIs
- Financial models, transactions, goals, debts, taxes, AI logic
- Frontend (Nuxt)
- Production hardening beyond sensible defaults
- Changing RFC-001 or inventing a parallel folder layout

---

## 4. Architecture Overview

- **Modular monolith** ([ADR-004](../../docs/adr/ADR-004-modular-monolith.md))
- **Domain modules** with identical internal layers ([ADR-007](../../docs/adr/ADR-007-domain-driven-modules.md), [backend-structure](../../docs/architecture/backend-structure.md))
- Package root: `wealthos` under `src/`
- Composition: `main.py` → `app/application.py` + `lifespan` + `router`
- Cross-cutting only in `core/` and thin `shared/`
- No global `controllers/` / `models/` / `services/` trees

Dependency direction inside modules (for later SPECs):

```
api → application → domain
infrastructure → domain
```

This SPEC only creates the scaffolding and platform wiring.

---

## 5. Deliverables

| # | Deliverable |
|---|-------------|
| D1 | Runnable FastAPI app via `uv` and via Docker Compose |
| D2 | Canonical `src/wealthos/` tree with empty modules |
| D3 | Settings + logging + DB engine/session |
| D4 | Alembic initialized + empty migration |
| D5 | `GET /` health JSON contract |
| D6 | Pytest + Ruff + pre-commit + CI workflow |
| D7 | Backend README documenting commands |

---

## 6. Directory Structure

```
backend/
├── pyproject.toml
├── uv.lock
├── README.md
├── Dockerfile
├── src/wealthos/
│   ├── main.py
│   ├── app/           # application.py, lifespan.py, router.py
│   ├── core/          # config, settings, security, database, logging, …
│   ├── shared/        # models, schemas, pagination, utils, events
│   └── modules/       # identity, finance, goals, debts, dashboard, taxes, ai
├── tests/
│   └── test_health.py
├── alembic/
│   └── versions/
└── scripts/
```

Each module includes: `api/`, `domain/`, `application/`, `infrastructure/`, `schemas/`, `tests/`, `__init__.py`.

Also at repo root: `docker-compose.yml`, `.env.example`.

---

## 7. Technologies

| Layer | Choice |
|-------|--------|
| Language | Python 3.13 |
| Package manager | uv |
| API | FastAPI + Uvicorn |
| Validation / settings | Pydantic v2 + pydantic-settings |
| ORM / DB | SQLAlchemy 2 + psycopg + PostgreSQL |
| Migrations | Alembic |
| Quality | Ruff, Pytest, httpx, pre-commit |
| Runtime packaging | Docker, Docker Compose |

---

## 8. Implementation Plan

Execute in order. Tick as you go.

### Phase A — Project bootstrap

- [ ] Create `backend/` uv project (`pyproject.toml`, `uv.lock`)
- [ ] Configure Ruff + Pytest in `pyproject.toml`
- [ ] Create `src/wealthos/` tree (app, core, shared, modules scaffolds)
- [ ] Add `backend/README.md`

### Phase B — App & configuration

- [ ] Implement settings / config from env
- [ ] Implement logging
- [ ] App factory + lifespan + root router
- [ ] Stub security, exceptions, dependencies
- [ ] SQLAlchemy engine + session

### Phase C — Data & containers

- [ ] Alembic init + empty baseline migration
- [ ] `backend/Dockerfile`
- [ ] Root `docker-compose.yml` (api + postgres)
- [ ] Update `.env.example`

### Phase D — Health & quality gates

- [ ] Implement `GET /` health payload
- [ ] Add `tests/test_health.py`
- [ ] Add pre-commit config
- [ ] Add GitHub Actions workflow (`ruff` → `pytest`)
- [ ] Verify Swagger `/docs`

---

## 9. Acceptance Criteria

On a clean machine / CI:

| # | Criterion |
|---|-----------|
| AC1 | `uv sync` succeeds in `backend/` |
| AC2 | App starts (`uv run uvicorn wealthos.main:app …` **or** `docker compose up`) |
| AC3 | Swagger available at `/docs` |
| AC4 | `GET /` → **200** with `{ "service": "wealthos-api", "version": "0.1.0", "status": "healthy" }` |
| AC5 | `alembic upgrade head` succeeds against Compose Postgres |
| AC6 | `uv run pytest` passes |
| AC7 | `uv run ruff check .` passes |
| AC8 | CI workflow exists and is green for the completing PR |
| AC9 | All listed modules exist as scaffolds |
| AC10 | No domain business logic beyond health / wiring |

---

## 10. Commit Plan

Use these commits (order fixed). Do not invent unrelated commit themes mid-SPEC.

| # | Message |
|---|---------|
| 1 | `build: initialize backend project` |
| 2 | `build: configure uv` |
| 3 | `build: configure FastAPI` |
| 4 | `build: configure SQLAlchemy` |
| 5 | `build: configure Alembic` |
| 6 | `build: configure Docker` |
| 7 | `test: add health endpoint tests` |
| 8 | `docs: update bootstrap documentation` |

Notes:

- Ruff / pre-commit / CI may land with commits 2, 7, or 8 — keep history readable; prefer attaching CI to commit 7 or 8 if not a separate plan line.
- When all ACs pass: mark Status **Completed** and announce **SPEC-001 Completed**.

---

## 11. Risks

| Risk | Mitigation |
|------|------------|
| Over-building empty modules | Scaffolds only; no domain code |
| Docker vs local drift | Same `uv.lock`; document both paths |
| Python 3.13 base image gaps | Pin known-good image; amend only via new SPEC if forced to 3.12 |
| Pre-commit too slow | CI remains source of truth; allow documented skip for emergencies |

---

## 12. Definition of Done

SPEC-001 is **Completed** when:

- [ ] All Acceptance Criteria (AC1–AC10) are met
- [ ] Commit Plan items are on `main` (or merged PR)
- [ ] Implementation checklist in §8 is fully `[x]`
- [ ] EPIC-001 exit criteria can be evaluated
- [ ] Status field set to **Completed**
- [ ] No further edits to this file except checkbox/status closure

**Next:** open SPECs under `specs/backend/identity/` (EPIC-002) — do not start Identity code in this SPEC.
