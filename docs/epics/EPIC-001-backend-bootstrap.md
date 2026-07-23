# EPIC-001

# Backend Bootstrap

**Status:** Planned  
**Parent:** [RFC-001 Backend Foundation](../rfc/RFC-001-backend-foundation.md) (Accepted)  
**Primary SPEC:** [SPEC-001 Backend Bootstrap](../../specs/backend/bootstrap/SPEC-001-backend-bootstrap.md)
**Related:** [Sprint 1 plan](../roadmap/sprint-1-backend-foundation.md)

---

## Outcome

A runnable WealthOS backend: uv project, domain-oriented layout, config, Postgres via Docker, Alembic, health API, tests, lint, and CI — **without** domain business logic.

---

## Workstreams (inside this Epic)

RFC-001 decomposes into six workstreams. They may map 1:1 to commits/sprints, but they share a single SPEC until we split SPECs further.

```
RFC-001
│
├── WS-1  Bootstrap Project
├── WS-2  Configuration
├── WS-3  Database
├── WS-4  Quality
├── WS-5  Docker
└── WS-6  Health API
```

| Workstream | Delivers | Suggested commit theme |
|------------|----------|------------------------|
| WS-1 Bootstrap Project | `uv`, `pyproject.toml`, package layout `src/wealthos/` | `build(backend): …` |
| WS-2 Configuration | settings, logging, core deps wiring | `feat(backend): …` |
| WS-3 Database | SQLAlchemy engine/session, Alembic baseline | `feat(backend): …` |
| WS-4 Quality | Ruff, Pytest, pre-commit, CI | `test` / `ci` / `chore` |
| WS-5 Docker | Dockerfile + Compose + `.env.example` | `build: …` |
| WS-6 Health API | `GET /` healthy JSON + OpenAPI | `feat(backend): …` |

---

## Non-goals

- Authentication / JWT flows
- Organization CRUD (beyond empty module scaffold)
- Transactions, goals, debts, taxes, AI logic
- Frontend

---

## Exit criteria

- [ ] SPEC-001 acceptance criteria all met
- [ ] Documented start command works on a clean machine
- [ ] CI green on `main`
- [ ] Ready to open EPIC-002 (Identity)

---

## Status tracking

Update when SPEC-001 tasks flip to `[x]`. Mark this Epic **Done** when exit criteria pass.
