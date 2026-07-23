# ADR-006: uv as the Python package manager

- **Status:** accepted
- **Date:** 2026-07-23
- **Deciders:** WealthOS core

## Context

The WealthOS backend is FastAPI/Python ([ADR-001](./ADR-001-fastapi.md)). We need a fast, reproducible way to manage dependencies, virtualenvs, and lockfiles for local development and CI — without the historical friction of mixing `pip`, `venv`, and ad-hoc scripts.

## Decision

Use **[uv](https://github.com/astral-sh/uv)** as the primary Python package manager and environment tool for `backend/`.

- Lock dependencies with uv’s lockfile workflow
- Create and sync local environments via uv
- Prefer uv commands in docs and CI over raw `pip install`

## Consequences

### Positive
- Fast installs and deterministic environments
- Simpler onboarding (`uv sync` style workflows)
- Good fit for modern FastAPI projects and CI caches

### Negative / trade-offs
- Contributors must install uv (or use a documented bootstrap)
- Ecosystem familiarity still catching up vs classic pip/poetry in some teams
- Must keep Docker/CI images aligned with the same lockfile

## Alternatives considered
- **pip + venv** — universal; slower and more manual lock/repro story
- **Poetry** — mature; heavier UX than uv for our needs
- **PDM / Hatch** — viable; uv preferred for speed and DX
