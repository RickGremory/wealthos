.PHONY: help sync dev infra-up infra-down migrate migration test lint format check

help:
	@echo "WealthOS backend targets:"
	@echo "  make sync        Install dependencies with uv"
	@echo "  make infra-up    Start Postgres/Redis/Mailpit"
	@echo "  make infra-down  Stop infrastructure"
	@echo "  make dev         Run API with reload"
	@echo "  make migrate     Apply Alembic migrations"
	@echo "  make migration   Create autogenerate revision (MSG=...)"
	@echo "  make test        Run pytest"
	@echo "  make lint        Ruff check"
	@echo "  make format      Ruff format"
	@echo "  make check       lint + test"

sync:
	uv sync

infra-up:
	docker compose -f ../docker-compose.yml up -d postgres redis mailpit

infra-down:
	docker compose -f ../docker-compose.yml down

dev:
	uv run uvicorn wealthos.main:app --reload --app-dir src --host 0.0.0.0 --port 8000

migrate:
	uv run alembic upgrade head

migration:
	uv run alembic revision --autogenerate -m "$(MSG)"

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

check: lint test
