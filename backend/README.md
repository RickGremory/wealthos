# WealthOS backend

Personal Finance Operating System for Independent Professionals — API.

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
cd backend
uv sync
```

## Verify

```bash
uv run python --version
uv run python -c "import fastapi, sqlalchemy, pydantic; print('WealthOS Bootstrap Ready')"
```

## Layout

```
src/wealthos/
  app/       # FastAPI composition (Pack 2)
  core/      # settings, db, logging
  shared/    # thin cross-cutting helpers
  modules/   # domains — added when needed (YAGNI)
```

Bootstrap Pack 1 establishes tooling and folders only — no HTTP server yet.
