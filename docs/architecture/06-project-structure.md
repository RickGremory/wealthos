# Project Structure

How the WealthOS repository is organized.

## Top-level layout

```
WealthOS/
├── .github/           # CI/CD, templates, CODEOWNERS, CONTRIBUTING, SECURITY
├── .ai/               # AI agent context, conventions, prompts
├── docs/
│   ├── adr/           # Architecture Decision Records
│   ├── rfc/           # Design proposals (RFCs)
│   ├── epics/         # Multi-week outcomes
│   ├── specs/         # Implementation SPECs
│   ├── architecture/  # System structure & principles
│   ├── product/       # Manifesto, vision, product principles
│   ├── engineering/   # Engineering standards & workflow
│   ├── roadmap/       # Delivery phases
│   ├── api/           # API / OpenAPI notes
│   ├── database/      # Schema & migration notes
│   └── decisions/     # Chronological decision log
├── journal/           # Working notes
├── prompts/           # Shared reusable prompts
├── specs/             # Product / technical specs
├── backend/           # FastAPI modular monolith
├── frontend/          # Nuxt web application
├── infrastructure/    # IaC, environments, deploy
├── scripts/           # Automation and utilities
├── docker-compose.yml
├── .editorconfig
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Documentation map (`docs/`)

| Path | Purpose |
|------|---------|
| `product/00-manifesto.md` | Why we exist |
| `product/01-product-vision.md` | Where we are going |
| `product/02-product-principles.md` | What we choose to build |
| `engineering/03-engineering-principles.md` | How we build |
| `architecture/04-architecture-principles.md` | System constraints |
| `decisions/05-decision-log.md` | Chronological decision index |
| `architecture/06-project-structure.md` | This file |
| `architecture/backend-structure.md` | Canonical backend tree + module template |
| `roadmap/07-development-roadmap.md` | Phased delivery plan |
| `roadmap/sprint-1-backend-foundation.md` | Sprint 1 executable plan (backend) |
| `roadmap/module-roadmap.md` | Domain module delivery order |
| `engineering/08-coding-standards.md` | Language and style rules |
| `engineering/09-git-workflow.md` | Branches, commits, PRs |
| `engineering/10-testing-strategy.md` | What and how we test |
| `engineering/11-delivery-workflow.md` | Vision → RFC → Epic → SPEC → PR |
| `epics/` | Multi-week work under RFCs |
| `specs/` | Implementation SPECs (e.g. SPEC-001) |
| `adr/` | Hard architecture decisions (ADRs) |
| `rfc/` | Design proposals (RFCs) |
| `api/` | API contract notes |
| `database/` | Schema / migration notes |

## Backend (`backend/`)

Modular monolith (see [ADR-004](../adr/ADR-004-modular-monolith.md), [ADR-007](../adr/ADR-007-domain-driven-modules.md)):

- One deployable FastAPI app ([ADR-001](../adr/ADR-001-fastapi.md))
- Internal modules / bounded contexts with clear ownership
- PostgreSQL as system of record ([ADR-005](../adr/ADR-005-postgresql.md))
- Python deps via uv ([ADR-006](../adr/ADR-006-uv-package-manager.md))

**Canonical tree and per-module layout:** [backend-structure.md](./backend-structure.md)

Expected package shape (summary):

```
backend/
├── src/wealthos/
│   ├── app/            # FastAPI factory, lifespan, root router
│   ├── core/           # settings, security, database, logging
│   ├── shared/         # cross-cutting helpers (not domain rules)
│   ├── modules/        # identity, finance, goals, debts, taxes, dashboard, ai
│   └── main.py
├── tests/
├── alembic/
├── scripts/
└── pyproject.toml
```

## Frontend (`frontend/`)

Nuxt app ([ADR-002](../adr/ADR-002-nuxt.md)):

- Talks to backend via explicit API contracts
- Does not invent financial truth
- Organization-scoped views and actions

## Domain invariants (everywhere)

From `.ai/project.md`:

- Transactions are the source of truth
- Goals never own money
- Everything belongs to an Organization
- Always use UUID
- Always use UTC timestamps

## Status

Scaffold only. Folder conventions above are the target as code lands.
