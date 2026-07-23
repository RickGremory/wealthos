# Sprint 1 — Backend Foundation

Plan ejecutable para bootstrap del backend WealthOS (FastAPI + uv + PostgreSQL).

**Objetivo del sprint:** tener un backend arrancable, testeable y con CI, con arquitectura por dominios (no capas técnicas globales).

**Relacionado:** [ADR-001](../adr/ADR-001-fastapi.md), [ADR-004](../adr/ADR-004-modular-monolith.md), [ADR-006](../adr/ADR-006-uv-package-manager.md), [ADR-007](../adr/ADR-007-domain-driven-modules.md), [roadmap general](./07-development-roadmap.md).

---

## Exit criteria (Sprint 1 completo)

- [ ] Proyecto Python con `uv` (`pyproject.toml`, `uv.lock`)
- [ ] Dependencias core instaladas
- [ ] Estructura por módulos de dominio
- [ ] Settings / logging / database
- [ ] Docker Compose + Dockerfile
- [ ] Alembic con migración inicial (vacía OK)
- [ ] `GET /` → health 200
- [ ] Pytest verde para health
- [ ] GitHub Actions: ruff + pytest
- [ ] Pre-commit: ruff + format + tests

---

## Sprint 1.1 — Bootstrap del repositorio Python

**Scope**

```
backend/
├── pyproject.toml
├── uv.lock
├── README.md
├── src/
└── tests/
```

**Commit**

```
build(backend): initialize Python project with uv
```

**Done when**

- [ ] `uv` inicializa el proyecto
- [ ] `src/` y `tests/` existen
- [ ] README mínimo del backend

---

## Sprint 1.2 — Dependencias

**Instalar**

- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- Pydantic Settings
- psycopg
- Pytest
- Ruff

**Commit**

```
build(backend): install project dependencies
```

**Done when**

- [ ] Dependencias en `pyproject.toml` / lockfile
- [ ] Importables en el entorno local

---

## Sprint 1.3 — Estructura por dominios

**Decisión importante:** no usar `controllers/`, `models/`, `services/`, `repositories/` en la raíz.

Usar **módulos de negocio** independientes (ver [ADR-007](../adr/ADR-007-domain-driven-modules.md) y el árbol canónico en [backend-structure.md](../architecture/backend-structure.md)).

**Target (resumen)**

```
backend/
├── src/wealthos/
│   ├── app/
│   ├── core/
│   ├── shared/
│   ├── modules/
│   │   ├── identity/
│   │   ├── finance/
│   │   ├── goals/
│   │   ├── debts/
│   │   ├── taxes/
│   │   ├── dashboard/
│   │   └── ai/
│   └── main.py
├── tests/
├── alembic/
└── scripts/
```

**Dentro de cada módulo** (misma plantilla; ejemplo `finance/`):

```
finance/
├── api/
├── domain/
├── application/
├── infrastructure/
├── schemas/
├── tests/
└── __init__.py
```

Cada módulo debe poder extraerse a microservicio en el futuro si el negocio lo justifica.

**Commit sugerido**

```
feat(backend): scaffold domain-oriented module layout
```

**Done when**

- [ ] Layout canónico documentado e inicializado bajo `src/wealthos/`
- [ ] `main.py` / app factory arrancan la app (aunque sea mínima)
- [ ] Sin estructura “tutorial” global de capas

---

## Sprint 1.4 — Configuración

Crear en `core/` (o equivalente):

- `settings.py`
- `config.py`
- `logging.py`
- `database.py`

**Commit sugerido**

```
feat(backend): add settings, logging, and database config
```

**Done when**

- [ ] Settings vía Pydantic Settings + env
- [ ] Logging configurado
- [ ] Engine/session SQLAlchemy listos

---

## Sprint 1.5 — Docker

- `docker-compose.yml` (raíz)
- `backend/Dockerfile`
- Actualizar `.env.example`

**Commit sugerido**

```
build: add backend Docker setup
```

**Done when**

- [ ] API + Postgres levantan con Compose
- [ ] Variables documentadas en `.env.example`

---

## Sprint 1.6 — Alembic

```
alembic/
└── versions/
```

Primera migración vacía (baseline).

**Commit sugerido**

```
feat(backend): initialize Alembic with empty migration
```

**Done when**

- [ ] `alembic upgrade head` funciona contra Postgres local

---

## Sprint 1.7 — Health check

`GET /` → `200 OK`

```json
{
  "service": "wealthos-api",
  "version": "0.1.0",
  "status": "healthy"
}
```

**Commit sugerido**

```
feat(backend): add health check endpoint
```

**Done when**

- [ ] Respuesta exacta (campos anteriores)
- [ ] Documentado en OpenAPI

---

## Sprint 1.8 — Pytest

Primer test: `GET /` → `200`.

**Commit sugerido**

```
test(backend): add health check test
```

**Done when**

- [ ] `pytest` pasa en local

---

## Sprint 1.9 — CI (GitHub Actions)

Pipeline:

```
ruff → pytest → success
```

**Commit sugerido**

```
ci: add backend lint and test workflow
```

**Done when**

- [ ] Workflow en `.github/workflows/`
- [ ] Verde en PR / push a `main`

---

## Sprint 1.10 — Pre-commit

En cada commit:

```
ruff → format → tests
```

**Commit sugerido**

```
chore: add pre-commit hooks for ruff, format, and tests
```

**Done when**

- [ ] `.pre-commit-config.yaml` (o equivalente)
- [ ] Hooks instalables y documentados en `backend/README.md`

---

## Orden de ejecución

```
1.1 Bootstrap uv
 → 1.2 Dependencies
 → 1.3 Domain modules
 → 1.4 Config
 → 1.5 Docker
 → 1.6 Alembic
 → 1.7 Health
 → 1.8 Pytest
 → 1.9 CI
 → 1.10 Pre-commit
```

## Notas

- Un commit por sub-sprint (como se indica), salvo que un paso sea demasiado pequeño para ir solo.
- No implementar lógica de dominio (finance/goals/etc.) en Sprint 1: solo el esqueleto.
- El dashboard sigue siendo el centro del producto (ADR-008); aquí solo se reserva el módulo.
