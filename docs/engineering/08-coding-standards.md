# Coding Standards

Shared standards for WealthOS code. See also `.ai/coding-style.md` and `docs/engineering/03-engineering-principles.md`.

## Universal rules

1. **UUID for identifiers** — no sequential public IDs for domain entities.
2. **UTC timestamps everywhere** — store and serialize in UTC; convert only at the UI edge.
3. **Organization scoping** — every domain record belongs to an Organization; queries must enforce it.
4. **Transactions are source of truth** — balances and reports derive from them; do not invent parallel ledgers casually.
5. **Goals never own money** — goals track targets/progress; funding always flows through transactions/accounts.
6. **No secrets in git** — use `.env` from `.env.example`.
7. **Small reviewable diffs** — one concern per PR when practical.

## Backend (FastAPI / Python)

- Prefer explicit Pydantic schemas for request/response contracts
- Keep route handlers thin; domain logic in services / module interiors
- Type hints on public functions
- Migrations for every schema change
- Money amounts: use precise decimal types — never float for currency
- Fail closed on ambiguous financial writes

## Frontend (Nuxt / Vue)

- Organization context available before money screens render
- Call typed API clients; do not hardcode ad-hoc URL shapes in components
- Presentation only — no domain rules that contradict the backend
- Prefer composables for shared state/fetch patterns
- Accessible forms and clear empty/error states for money data

## Naming

- Files/modules: clear domain nouns (`transactions`, `organizations`, `goals`)
- Avoid abbreviations that hide money meaning (`amt`, `txn` only if already pervasive)
- ADR and doc cross-links when behavior encodes a decision

## Formatting & lint

- Backend: ruff / formatter once tooling is added in `backend/`
- Frontend: ESLint + Prettier (or Nuxt defaults) once scaffolding lands
- CI must fail on lint errors for touched packages

## Comments & docs

- Comment *why*, not *what*
- Update `specs/` when user-visible behavior changes
- Update ADRs when architecture changes — do not silently diverge

## Status

Draft. Tooling pins (exact linters/versions) land with Phase 1 skeleton.
