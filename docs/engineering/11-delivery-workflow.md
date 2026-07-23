# Delivery Workflow

How WealthOS turns vision into merged code.

Inspired by **Shape Up** (appetite / betting) and **Scrum** (sprints / review), simplified for a small team — and designed so a future hire can onboard by reading documents, not archaeology.

---

## Hierarchy

```
Vision          → why we exist (docs/product/)
    ↓
ADR             → irreversible technical decisions (docs/adr/)
    ↓
RFC             → large initiative / technical contract (docs/rfc/)
    ↓
Epic            → weeks of related work (docs/epics/)
    ↓
SPEC            → exact implementation plan (docs/specs/)
    ↓
Sprint / Tasks  → days of execution (checklists inside SPECs)
    ↓
Commits → PR → Merge
```

| Artifact | Answers | Lifetime | Change policy |
|----------|---------|----------|---------------|
| Vision / Principles | Why / what kind of product | Years | Rare, deliberate |
| ADR | What we decided and why | Permanent (may supersede) | New ADR if reversed |
| RFC | What we want to build (initiative) | Months | **Freeze when Accepted** |
| Epic | Chunk of the RFC by outcome | Weeks | Update status / links |
| SPEC | Exactly how we build a slice | Days–weeks | Checklist ticks; amend only if blocked |
| Sprint | What we execute now | Days | Operational |

---

## Roles of each document

### RFC — technical contract

An RFC is **not a task**. Once **Accepted**, it is the contract for the initiative.

- Does not get rewritten as implementation details grow
- Decomposes into Epics
- Points to ADRs it depends on

Example: [RFC-001 Backend Foundation](../rfc/RFC-001-backend-foundation.md) — Accepted. Do not expand it with bootstrap checklists; that belongs in SPECs.

### Epic — functional grouping

An Epic groups related work that delivers a coherent outcome (bootstrap, identity, transactions, dashboard).

- Links parent RFC
- Lists child SPECs
- Tracks high-level status

### SPEC — implementation contract

A SPEC answers **how exactly** we will build a slice:

- Folder trees to create
- Dependencies and config
- Acceptance criteria
- Suggested commits
- Checkbox tasks (`[ ]` → `[x]`)

When a SPEC is approved, coding starts. Mark tasks as you go so progress is always visible.

### Sprint

A sprint executes one or more SPECs (or a subset of a SPEC). Sprint plans may live in `docs/roadmap/` for scheduling; the source of truth for *what* to build remains the SPEC.

---

## Working loop (from today)

1. **Approve RFC** (or confirm it is already Accepted)
2. **Open Epic(s)** under `docs/epics/`
3. **Write SPEC** under `docs/specs/...` (3–5 pages, actionable)
4. **Approve SPEC**
5. **Implement** with small commits matching the SPEC
6. **PR** using the checklist (tests, docs, ADR if needed)
7. **Merge** and tick SPEC items to `[x]`

Do **not** invent `pyproject.toml` before the relevant SPEC is approved.

---

## Folder map

```
docs/
├── adr/              # Decisions
├── rfc/              # Initiatives / contracts
├── epics/            # Multi-week outcomes
├── specs/            # Implementation plans
│   └── backend/
│       └── bootstrap/
├── architecture/     # Canonical structures & principles
├── product/          # Vision & product principles
├── engineering/      # Engineering standards & this workflow
└── roadmap/          # Phases, sprints, module order
```

Root `specs/` (if present) is reserved for future product-facing specs or should point here — **implementation SPECs live under `docs/specs/`**.

---

## Naming

| Type | Pattern | Example |
|------|---------|---------|
| RFC | `RFC-NNN-short-title.md` | `RFC-001-backend-foundation.md` |
| Epic | `EPIC-NNN-short-title.md` | `EPIC-001-backend-bootstrap.md` |
| SPEC | `SPEC-NNN-short-title.md` | `SPEC-001-backend-bootstrap.md` |

---

## Why this scales

If another developer joins in a year:

> Read the RFC, the Epic, and the SPEC.

They get strategy, scope, and exact build steps — without reconstructing chat history.

That is the documentation WealthOS deserves as a professional SaaS learning project.
