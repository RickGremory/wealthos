# Project Structure

How the WealthOS repository is organized.

## Top-level layout

```
WealthOS/
├── .github/           # CI/CD, templates, CODEOWNERS, CONTRIBUTING, SECURITY
├── .ai/               # AI agent context, conventions, prompts
├── docs/
│   ├── adr/           # Architecture Decision Records
│   ├── rfc/           # Initiative contracts (frozen when Accepted)
│   ├── epics/         # Multi-week outcomes
│   ├── architecture/  # System structure & principles
│   ├── product/       # Manifesto, vision, product principles
│   ├── engineering/   # Standards & delivery workflow
│   ├── roadmap/       # Phases / sprint notes
│   ├── api/           # API / OpenAPI notes
│   ├── database/      # Schema & migration notes
│   └── decisions/     # Small product/strategy decisions (dated)
├── specs/             # Execution SPECs (sprint contracts) ★
│   ├── backend/
│   ├── frontend/
│   └── infrastructure/
├── planning/          # Backlog, roadmap, milestones, releases
├── journal/           # Working notes
├── prompts/           # Shared reusable prompts
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

★ A SPEC is the document open while coding. Completed SPECs are immutable.

## Documentation map (`docs/`)

| Path | Purpose |
|------|---------|
| `product/00-manifesto.md` | Why we exist |
| `product/01-product-vision.md` | Where we are going |
| `product/02-product-principles.md` | What we choose to build |
| `engineering/03-engineering-principles.md` | How we build |
| `architecture/04-architecture-principles.md` | System constraints |
| `decisions/` | Product decisions + index log |
| `architecture/06-project-structure.md` | This file |
| `architecture/backend-structure.md` | Canonical backend tree + module template |
| `roadmap/` | Phases, sprint notes, module order |
| `engineering/11-delivery-workflow.md` | Vision → RFC → Epic → SPEC → PR |
| `epics/` | Multi-week work under RFCs |
| `adr/` | Hard architecture decisions |
| `rfc/` | Design proposals (RFCs) |

## Execution & planning (repo root)

| Path | Purpose |
|------|---------|
| `specs/` | SPEC-NNN execution contracts by area |
| `planning/BACKLOG.md` | What might come next |
| `planning/ROADMAP.md` | Product sequence |
| `planning/MILESTONES.md` | Named outcomes |
| `planning/RELEASES.md` | What shipped |

## Backend (`backend/`)

Modular monolith (see [ADR-004](../adr/ADR-004-modular-monolith.md), [ADR-007](../adr/ADR-007-domain-driven-modules.md)):

- One deployable FastAPI app ([ADR-001](../adr/ADR-001-fastapi.md))
- Internal modules / bounded contexts with clear ownership
- PostgreSQL as system of record ([ADR-005](../adr/ADR-005-postgresql.md))
- Python deps via uv ([ADR-006](../adr/ADR-006-uv-package-manager.md))

**Canonical tree and per-module layout:** [backend-structure.md](./backend-structure.md)

**Current execution plan:** [SPEC-001](../../specs/backend/bootstrap/SPEC-001-backend-bootstrap.md)

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

Scaffold + documentation. Application code starts after SPEC-001 is Accepted.
