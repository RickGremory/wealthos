# WealthOS backend

Personal Finance Operating System for Independent Professionals — API.

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)
- Docker (for Postgres / Redis / Mailpit)

## Setup

```bash
cd backend
cp .env.example .env
uv sync
```

From repo root (or `make infra-up` in backend):

```bash
docker compose up -d postgres redis mailpit
```

## Day-to-day

```bash
cd backend
make dev        # API + reload
make test
make lint
make format
make migrate    # after Postgres is healthy
```

- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health
- Organizations API: http://127.0.0.1:8000/api/v1/organizations
- Mailpit UI: http://127.0.0.1:8025
- Postgres (host): `localhost:5433` (user/pass/db: `wealthos`)
- pgAdmin (optional): `docker compose --profile tools up -d pgadmin` → http://127.0.0.1:5050

## Layout

```
src/wealthos/
  main.py              # boring entrypoint
  app/                 # application assembly
  core/                # settings, database, logging, dependencies
  shared/
  modules/             # domains (YAGNI)
alembic/               # migrations (wired to Settings + Base)
docker/                # postgres init, redis placeholders
scripts/               # thin shell wrappers
```

## Modules

Generate a new domain module:

```bash
uv run python scripts/create_module.py accounts
```

Then add `"accounts"` to `MODULES` in `src/wealthos/modules/__init__.py`.

Standards: `docs/engineering/CODING_STANDARDS.md`.

## Stabilization / perf

```bash
make perf-seed      # 50k transactions for load-test org
make perf-explain   # EXPLAIN ANALYZE → perf/explain/latest
make perf-bench     # p50/p95 dashboard + goals
```

See `docs/engineering/12-stabilization.md`.
