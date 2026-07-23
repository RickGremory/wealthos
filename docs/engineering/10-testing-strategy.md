# Testing Strategy

What we test, why, and how deep — especially around money.

## Goals

- Protect financial truth (transactions → derived balances/reports)
- Catch Organization isolation bugs early
- Keep feedback fast enough for daily development

## Test layers

### 1. Unit

- Domain pure functions and calculators (tax reserve helpers, goal progress, debt schedules)
- Schema/DTO validation edge cases
- Fast, no network, no real DB when avoidable

### 2. Integration

- FastAPI routes + PostgreSQL (test DB)
- Migrations apply cleanly
- Organization scoping on read/write paths
- Transaction writes update derived views correctly

### 3. Contract / API

- OpenAPI-compatible request/response shapes
- Auth and Organization headers/claims behavior
- Error codes for forbidden cross-org access

### 4. Frontend

- Component tests for critical forms (create transaction, goal setup)
- Page/smoke tests for auth → organization home
- Do not duplicate backend domain rules in frontend tests

### 5. End-to-end (later)

- Happy path: sign in → record transactions → see cashflow / goal progress
- Add when Phase 2 ledger exists; keep a thin critical path, not a UI encyclopedia

## Non-negotiable cases

| Area | Must verify |
|------|-------------|
| Transactions | Create/list; balances derive correctly; no silent overwrite of history |
| Organization | User A cannot read/write User B’s org data |
| Goals | Progress updates without goals “owning” balances |
| Time | Stored timestamps are UTC; no local-tz leakage in persistence |
| IDs | UUIDs used for public/domain identifiers |

## Money-specific rules

- Prefer decimal/precise types in fixtures — never float cash amounts
- Include timezone-boundary cases when date filters matter
- Regression tests for any production money bug

## Tooling (target)

| Layer | Backend | Frontend |
|-------|---------|----------|
| Unit | pytest | Vitest (or Nuxt default) |
| Integration | pytest + test Postgres | — |
| E2E | — | Playwright (later) |
| CI | run on PR via `.github/workflows/` | same |

## Coverage philosophy

- High confidence on ledger and org isolation
- Do not chase 100% line coverage on UI chrome
- A failing money test blocks merge

## Status

Draft. Concrete commands and CI jobs land with Phase 1 skeleton.
