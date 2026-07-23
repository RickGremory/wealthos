# ADR-007

# Organize Backend by Business Domains

**Status:** Accepted

---

## Decision

Organize modules around business capabilities under `src/wealthos/modules/`.

Example modules:

```
identity/
finance/
goals/
debts/
taxes/
dashboard/
ai/
```

Each module uses the same internal layout (`api/`, `domain/`, `application/`, `infrastructure/`, …).

Full tree: [docs/architecture/backend-structure.md](../architecture/backend-structure.md).

---

## Avoid

```
controllers/
services/
models/
```

at the repository root (or as the global organizing principle).

---

## Motivation

Business domains change less frequently than technical implementations.

Identical module shapes make extraction to services possible later without a rewrite.
