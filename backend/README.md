# WealthOS backend

Personal Finance Operating System for Independent Professionals — API.

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
cd backend
cp .env.example .env
uv sync
```

## Run (Bootstrap Pack 2)

```bash
uv run uvicorn wealthos.main:app --reload --app-dir src
```

- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Layout

```
src/wealthos/
  main.py          # boring entrypoint
  app/             # application assembly
  core/            # settings / config
  shared/          # thin helpers
  modules/         # domains (YAGNI)
```
