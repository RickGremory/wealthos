# Development Roadmap

Phased plan to go from scaffold to a usable WealthOS core.

## North star

Help independent professionals convert income into wealth — with clarity on cashflow, taxes, debt, goals, and net worth.

## Phase 0 — Foundations (current)

- Repo layout, docs spine, ADRs
- Local tooling: Docker Compose, `.env.example`, git workflow
- Decide module boundaries for the modular monolith

**Exit criteria:** contributors can clone, read docs, and know the stack.

## Phase 1 — Platform skeleton

- FastAPI app boot + health endpoints
- PostgreSQL + migrations
- Organization + User identity (UUID, UTC everywhere)
- Nuxt shell: auth gate, layout, empty organization home
- CI: lint + unit smoke on PR

**Exit criteria:** signed-in user belongs to an Organization; empty app loads.

## Phase 2 — Ledger core

- Accounts and balances derived from transactions
- Transaction create / list / categorize (source of truth)
- Basic cashflow views
- Audit-friendly immutable money events (append-friendly history)

**Exit criteria:** user can record income/expense and see coherent balances.

## Phase 3 — Clarity loop

- Tax reserve estimates (rules configurable, explainable)
- Debt tracking and payoff visibility
- Goals as targets (goals never hold/own money — they reference funded progress)
- Simple net-worth snapshot

**Exit criteria:** user answers “where does money go?” and “am I closer to X?”

## Phase 4 — Decision support

- Decision / journal hooks tied to material money events
- Budgets or allocations that still settle via transactions
- Export / reporting basics

**Exit criteria:** decisions leave a trail; reports are traceable to transactions.

## Phase 5 — Open-core SaaS hardening

- Multi-tenant hardening for Organizations
- Hosted product packaging vs open core ([ADR-003](../adr/ADR-003-open-core.md))
- Backups, observability, rate limits, security review

**Exit criteria:** safe to run as a hosted MVP for early users.

## Explicit non-goals (near term)

- Investment advice or return guarantees
- Full accounting suite / double-entry ERP parity
- Microservices (stay modular monolith until forced otherwise)

## How we update this roadmap

- Material scope changes → entry in `docs/decisions/05-decision-log.md` and/or a new ADR
- Specs for slices live in `specs/` before large implementation

## Status

Draft roadmap. Dates and owners TBD.
