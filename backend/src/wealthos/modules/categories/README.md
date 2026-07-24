# Categories

## Purpose

Classify financial movements as income or expense within an organization, with optional two-level hierarchy (root → subcategory).

## Responsibilities

- CRUD-lite for categories (create, list, get, update, archive)
- System seed catalog on organization registration
- Tenant isolation and role-based write controls

## Public API

- `POST /api/v1/organizations/{organization_id}/categories`
- `GET /api/v1/organizations/{organization_id}/categories`
- `GET /api/v1/organizations/{organization_id}/categories/{category_id}`
- `PATCH /api/v1/organizations/{organization_id}/categories/{category_id}`
- `POST /api/v1/organizations/{organization_id}/categories/{category_id}/archive`
