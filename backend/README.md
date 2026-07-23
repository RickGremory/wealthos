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
- Mailpit UI: http://127.0.0.1:8025
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

## Foundation Kit notes

Infrastructure Pack elevates the downloaded starter stubs into a reusable SaaS base:
healthchecked Compose services, pooled SQLAlchemy sessions, Alembic + Settings, Makefile DX.
Async SQLAlchemy can land later without changing the module layout.
