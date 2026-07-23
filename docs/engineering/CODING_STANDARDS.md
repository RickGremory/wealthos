# WealthOS Coding Standards

Engineering style guide for building modules consistently.

See also: [Engineering Principles](./03-engineering-principles.md), [Backend Structure](../architecture/backend-structure.md), [ADR-007](../adr/ADR-007-domain-driven-modules.md).

---

## 1. Principles

- Small modules with one business capability each
- One responsibility per class / file
- **CQRS light** — prefer Commands and Queries over god-Services
- Domain layer is pure Python — **never imports SQLAlchemy or FastAPI**
- Infrastructure knows the domain; domain never knows infrastructure
- Every new domain starts with `scripts/create_module.py`

---

## 2. Standard module layout

```
modules/<name>/
├── api/
│   ├── router.py
│   └── dependencies.py
├── application/
│   ├── commands/
│   ├── queries/
│   └── services/          # only when orchestration spans multiple commands/queries
├── domain/
│   ├── entities/
│   ├── repositories/      # interfaces (protocols / ABCs)
│   ├── value_objects/
│   └── exceptions.py
├── infrastructure/
│   ├── models/            # SQLAlchemy
│   ├── repositories/      # implementations
│   └── mappers/
├── schemas/               # Pydantic API DTOs
├── tests/
└── README.md
```

Generate with:

```bash
cd backend
uv run python scripts/create_module.py accounts
```

Then register the name in `wealthos.modules.MODULES`.

---

## 3. When to create what

| Artifact | Create when |
|----------|-------------|
| **Command** | A write/intent that changes state (`create_organization.py`) |
| **Query** | A read that returns data without mutating (`list_organizations.py`) |
| **Service** | Rare — coordinates multiple commands/queries or external ports |
| **Entity** | A domain concept with identity and invariants |
| **Value object** | Immutable concept without identity (Money, Email) |
| **Repository interface** | Domain needs persistence without knowing SQL |
| **Model** | SQLAlchemy table mapping |
| **Mapper** | Convert Model ↔ Entity |
| **Schema** | HTTP request/response contracts (Pydantic) |

Avoid a single `UserService` that grows to 800 lines.

---

## 4. Naming

| Kind | Convention | Example |
|------|------------|---------|
| Module folder | plural snake | `organizations`, `transactions` |
| Command file | verb_noun | `create_organization.py` |
| Query file | verb_noun | `list_organizations.py` |
| Entity class | singular Pascal | `Organization` |
| SQLAlchemy model | `*Model` | `OrganizationModel` |
| Repository | `*Repository` | `OrganizationRepository` |
| Schema | `*Create`, `*Read`, `*Update` | `OrganizationCreate` |
| API tag / prefix | module name | `/organizations` |

---

## 5. Layer rules

### `api/`

- Thin: parse HTTP → call command/query → return schema
- No business rules
- No direct SQLAlchemy queries

### `application/`

- Use cases
- Commands mutate; queries read
- Depend on domain ports (repository interfaces), not infrastructure concretes (wire in deps)

### `domain/`

- Pure Python
- Invariants and exceptions
- No `Column`, no `Session`, no `APIRouter`

### `infrastructure/`

- SQLAlchemy models, repository implementations, mappers
- Organization scoping filters belong here **and** must be enforced on every query

### `schemas/`

- Pydantic v2 DTOs for OpenAPI
- Never leak ORM models in responses

---

## 6. Shared bases (`shared/base/`)

Use:

- `BaseRepository` — session + common CRUD helpers
- `BaseMapper` — model ↔ entity conversion contract
- `BaseService` — optional orchestration helper
- `BaseResponse` — envelope helpers when needed

Do not copy-paste session handling into every module.

---

## 7. Router registry

Do **not** manually `include_router` forever in `application.py`.

1. Add module name to `MODULES` in `wealthos/modules/__init__.py`
2. Ensure `modules/<name>/api/router.py` exports `router`
3. `register_modules(app)` loads them

Platform routes (e.g. `/health`) stay in `wealthos.app.router`.

---

## 8. Tests

- Prefer tests under `modules/<name>/tests/` for domain/application
- Cross-cutting / health stay in `backend/tests/`
- Name tests after behavior: `test_create_organization_rejects_blank_name`
- Money paths require coverage before merge

---

## 9. Migrations

- Alembic only — no ad-hoc DDL in app code
- One logical change per revision when practical
- Models live in module `infrastructure/models/`; ensure metadata import for autogenerate

---

## 10. Commits & PRs

Follow `.github/CONTRIBUTING.md` prefixes (`feat`, `fix`, `build`, …).

PRs that add a module must include:

- [ ] Generated structure (or equivalent)
- [ ] Module `README.md`
- [ ] Entry in `MODULES` if exposed via HTTP
- [ ] Tests for happy path + one failure path
- [ ] OpenAPI-visible schemas for public endpoints

---

## 11. Domain invariants (always)

- UUID identifiers
- UTC timestamps
- Everything belongs to an Organization (tenant boundary)
- Transactions are the source of truth
- Goals never own money
