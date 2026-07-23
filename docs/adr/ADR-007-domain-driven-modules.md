# ADR-007

# Organize Backend by Business Domains

**Status:** Accepted

---

## Decision

Organize modules around business capabilities.

Example

```
finance/
goals/
debts/
identity/
```

---

## Avoid

```
controllers/
services/
models/
```

at the repository root.

---

## Motivation

Business domains change less frequently than technical implementations.
