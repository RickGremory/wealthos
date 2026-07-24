# Goals

## Purpose

Track financial objectives without storing money. Progress is always derived
from accounts, manual progress rows, or organization net worth.

## Responsibilities

- Create and update goals (`manual`, `linked_accounts`, `net_worth_percentage`)
- Derive `GoalProgress` via `GoalProgressService` (single calculation path)
- Soft-archive goals; auto-complete when progress reaches 100%
- Enforce same-currency linking (no FX yet)

## Public API

Nested under `/api/v1/organizations/{organization_id}`:

- `POST /goals`
- `GET /goals`
- `GET /goals/{id}`
- `PATCH /goals/{id}`
- `POST /goals/{id}/archive`
- `POST /goals/{id}/manual-progress`

Dashboard:

- `GET /dashboard/goals`
- `GET /dashboard/summary` includes `goals: { active, completed }`

## Notes

Strategy is immutable after create. Linked accounts must match the goal currency.
