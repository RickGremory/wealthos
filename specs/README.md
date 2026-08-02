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
| [SPEC-002](./backend/debts/SPEC-002-financial-commitments.md) | Financial Commitments (E2E) | backend + frontend | Accepted |
| [SPEC-003](./backend/timeline/SPEC-003-financial-timeline.md) | Financial Timeline | backend + frontend | Completed |
| [SPEC-004](./backend/planning/SPEC-004-planning-safe-to-spend.md) | Planning & Safe To Spend | backend + frontend | Completed |
| [SPEC-005](./backend/recurring/SPEC-005-recurring-engine.md) | Recurring Engine | backend + frontend | Ready |
