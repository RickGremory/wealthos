# Engineering Principles

How we build and change the system.

## 1. Small, reviewable changes
Prefer diffs a human can reason about in one sitting.

## 2. Specs before sprawl
Material behavior belongs in `specs/` (or an ADR) before it becomes tribal knowledge.

## 3. Explicit contracts
Frontend and backend communicate through clear APIs / DTOs — not implied shape.

## 4. No secrets in the repo
Config via `.env` (from `.env.example`). Never commit credentials, keys, or dumps.

## 5. Test the money path
Anything that calculates, stores, or moves financial truth needs coverage and regression safety.

## 6. Operability counts
Logs, migrations, and failure modes are part of the feature — not leftovers.

## 7. Match the house style
Follow `.ai/coding-style.md` and existing patterns before inventing new ones.

## Status
Draft. Stack is FastAPI + Nuxt + PostgreSQL; language-specific tooling pins land with Phase 1 skeleton.
