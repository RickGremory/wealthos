# WealthOS

> The Financial Operating System for Independent Professionals.

WealthOS is an open-core platform that helps independent professionals organize their finances, build wealth, and make better financial decisions.

Unlike traditional expense trackers, WealthOS focuses on financial clarity, long-term goals, taxes, debt management, and wealth creation.

> [!IMPORTANT]
> WealthOS is under active development and is **not yet recommended for storing production financial data.**

---

## Preview

![WealthOS Dashboard](docs/assets/dashboard.png)

| Dashboard (mobile) | Transactions | Goals |
| --- | --- | --- |
| ![Mobile dashboard](docs/assets/dashboard-mobile.png) | ![Transactions](docs/assets/transactions.png) | ![Goals](docs/assets/goals.png) |

---

## Why?

Most independent professionals earn good money...

But very few understand:

- where it goes
- how much they actually own
- whether they're getting closer to buying a home
- how much they should reserve for taxes
- whether today's decisions are hurting tomorrow

WealthOS exists to solve that problem.

---

## Core Features

- Multi-organization financial workspaces
- Financial accounts and real-time balances
- Income, expense, transfer, and adjustment transactions
- Financial categories and hierarchies
- Net-worth and cash-flow dashboard
- Financial goals with account-linked progress
- Multi-currency separation (no silent FX conversion)
- Versioned legal consent and privacy settings
- Responsive desktop and mobile interface

---

## Technology

### Backend

- Python 3.13+
- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Alembic
- Pytest

### Frontend

- Nuxt 3
- Vue 3
- TypeScript
- Pinia
- Vitest / Playwright

### Architecture

- Modular monolith
- Domain-driven design
- Repository pattern
- CQRS-inspired read projections (dashboard)
- OpenAPI-generated frontend types

See `docs/` and `docs/adr/` for product and architecture decisions.

---

## Open-Core Model

The core financial platform is open source under the [MIT License](./LICENSE).

Future hosted or commercial capabilities may include:

- Managed cloud hosting
- Advanced tax integrations
- AI-powered financial insights
- Team and advisor collaboration
- Premium reporting and automation

See [ADR-003](./docs/adr/ADR-003-open-core.md).

---

## Project Status

WealthOS is currently in **active development**.

### Implemented

- Authentication and organization onboarding
- Versioned terms / privacy acceptance
- Financial accounts and categories
- Income, expense, transfer, and adjustment transactions
- Financial dashboard (multi-currency metrics)
- Goal tracking (manual, linked accounts, net worth)
- Responsive desktop and mobile interface

### In progress / next modules

- Product review and polish (responsive, a11y, consistency)
- Debt management UI
- Tax planning UI
- Budgets and cash-flow planning UI
- Recurring transactions
- Deeper privacy tooling (ARCO workflows, account deletion)

---

## Current Milestone

The current milestone focuses on product review, responsive behavior,
privacy policies, legal consent, and stabilization of the first usable
financial workflow (accounts → transactions → dashboard → goals).

---

## Local Development

### Requirements

- Docker (Postgres, Redis, Mailpit)
- Python 3.13+ with [uv](https://github.com/astral-sh/uv)
- Node.js 20+ with npm

### 1. Start infrastructure

```bash
cp .env.example .env
docker compose up -d
```

### 2. Backend

```bash
cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn wealthos.main:app --reload --app-dir src --host 0.0.0.0 --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev -- --host 127.0.0.1 --port 3000
```

App: [http://127.0.0.1:3000](http://127.0.0.1:3000)

### Useful checks

```bash
# Frontend
cd frontend && npm run lint && npm run typecheck && npm run test

# Backend
cd backend && uv run ruff check . && uv run pytest
```

---

## Repository

```
WealthOS/
├── .github/
├── .ai/
├── docs/              # strategy, ADRs, product principles
│   └── assets/        # README screenshots
├── specs/             # execution SPECs
├── planning/          # backlog, roadmap, milestones
├── adr/               # architecture decision records (repo root copies)
├── backend/           # FastAPI modular monolith
├── frontend/          # Nuxt 3 application
├── infrastructure/
├── scripts/
├── docker-compose.yml
└── README.md
```

Public legal pages (when running locally): `/legal`, `/legal/privacy`, `/legal/terms`, `/legal/cookies`.

---

## Vision

Become the operating system for personal finance.
