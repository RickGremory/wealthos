# Git Workflow

How we branch, commit, review, and ship.

## Default branch

- `main` is the integration branch and should remain releasable
- Protect `main` with PR reviews once the team grows beyond solo work

## Branch naming

```
feature/<short-description>
fix/<short-description>
chore/<short-description>
docs/<short-description>
```

Examples: `feature/org-uuid-model`, `fix/transaction-timezone`, `docs/roadmap-phase-1`.

## Commits

- Prefer focused commits with a clear *why*
- Message style: short imperative summary (1–2 sentences in body if needed)
- Never commit secrets, dumps, or `.env`
- Do not mix unrelated refactors with feature work

## Pull requests

Use `.github/PULL_REQUEST_TEMPLATE.md`:

- Summary of change and motivation
- Type of change
- Test plan checklist

PR expectations:

- Links to relevant `specs/` or ADR when behavior/architecture changes
- Screenshots for UI-visible changes when useful
- Small enough to review in one sitting when possible

## Review bar (money software)

- Organization scoping cannot be bypassed
- UUID + UTC conventions respected
- Transactions remain source of truth
- Goals do not hold balances / own money
- Migrations included when schema changes

## Merge

- Squash or merge — pick one team convention once CI exists; until then prefer clean history on `main`
- Delete feature branches after merge

## Releases (later)

- Tag semantic versions when we ship hosted builds
- Open-core vs commercial packaging noted per [ADR-003](../adr/ADR-003-open-core.md)

## Status

Draft workflow. Branch protection and required checks TBD in `.github/workflows/`.
