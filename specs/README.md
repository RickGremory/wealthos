# Specs

Execution plans for WealthOS. A SPEC is the **sprint contract** — open while coding, frozen when Completed.

See [Delivery Workflow](../docs/engineering/11-delivery-workflow.md).

## Rules

- Versioned: `SPEC-001`, `SPEC-002`, …
- Always use the **12-section** template
- **Never rewrite** a Completed SPEC — open a new one
- One Commit Plan per SPEC

## Layout

```
specs/
├── backend/
│   ├── bootstrap/
│   ├── identity/
│   ├── organizations/
│   ├── accounts/
│   ├── transactions/
│   └── ...
├── frontend/
└── infrastructure/
```

## Index

| SPEC | Title | Area | Status |
|------|-------|------|--------|
| [SPEC-001](./backend/bootstrap/SPEC-001-backend-bootstrap.md) | Backend Bootstrap | backend | Draft |
