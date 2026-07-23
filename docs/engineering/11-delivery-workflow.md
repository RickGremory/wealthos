# Delivery Workflow

How WealthOS turns vision into merged code.

We keep strategy documents (Vision → Principles → ADR → RFC), but **day-to-day work is driven by SPECs**.

A SPEC is not “more documentation”. It is the **execution plan** open while we develop — the contract between Architecture and Development.

---

## Two layers

### Strategy (write rarely, freeze when accepted)

```
Vision → Principles → ADR → RFC → Epic
```

### Execution (write before coding, tick while coding)

```
SPEC → Commits → Tests → PR → Merge → Close SPEC
```

| Artifact | Answers | Mutable after close? |
|----------|---------|----------------------|
| Vision / Principles | Why / product shape | Rarely |
| ADR | Hard technical decisions | Only via superseding ADR |
| RFC | Large initiative contract | **No** once Accepted |
| Epic | Weeks of related outcome | Status only |
| **SPEC** | Exactly what we build this sprint | **No** once Completed — open a new SPEC |
| Product `decisions/` | Small strategic “why” notes | Append-only dated files |
| `planning/` | Backlog, roadmap, releases | Living |

---

## What a SPEC must answer

1. What are we building?
2. Which files will we create?
3. Which technologies are involved?
4. Which dependencies exist?
5. What are the acceptance criteria?
6. Which commits do we expect?
7. What is out of this sprint?

### Required 12 sections

1. Objective  
2. Scope  
3. Out of Scope  
4. Architecture Overview  
5. Deliverables  
6. Directory Structure  
7. Technologies  
8. Implementation Plan  
9. Acceptance Criteria  
10. Commit Plan  
11. Risks  
12. Definition of Done  

---

## SPEC immutability

- SPECs are versioned: `SPEC-001`, `SPEC-002`, …
- While **Draft** / **Accepted** (in progress): checkboxes may flip `[ ]` → `[x]`
- When **Completed**: freeze the document
- If requirements change later: **create a new SPEC** — never rewrite history

Why: in two years we can read exactly how we thought in Sprint 1.

---

## Commit methodology

Each SPEC owns its commits. Prefer the SPEC’s Commit Plan over ad-hoc messages.

Example (SPEC-001):

1. `build: initialize backend project`  
2. `build: configure uv`  
3. …  
8. `docs: update bootstrap documentation`  

When the plan is done: **SPEC-001 Completed**.

---

## Folder map

```
specs/                         # Execution plans (canonical)
├── backend/
│   ├── bootstrap/
│   │   └── SPEC-001-backend-bootstrap.md
│   ├── identity/
│   ├── organizations/
│   ├── accounts/
│   ├── transactions/
│   └── ...
├── frontend/
└── infrastructure/

docs/
├── adr/                       # Architecture decisions
├── rfc/                       # Initiative contracts
├── epics/                     # Multi-week groupings
├── decisions/                 # Small product/strategy decisions (dated)
├── architecture/
├── product/
├── engineering/
└── roadmap/

planning/                      # Startup backlog view
├── BACKLOG.md
├── ROADMAP.md
├── RELEASES.md
└── MILESTONES.md
```

---

## Working loop (from now on)

1. Design a SPEC (12 sections)  
2. Review / Accept  
3. Implement together (SPEC open)  
4. Test  
5. Update docs if needed  
6. Close the Sprint / mark SPEC **Completed**  

Do not invent code before the SPEC is Accepted.

---

## How we communicate while building

Two response modes during implementation:

| Mode | Purpose |
|------|---------|
| **Architect Notes** | Why we chose this; future impact |
| **Implementation** | Concrete steps and code |

Both matter: WealthOS should ship a SaaS **and** teach the decisions behind it.

See also `.ai/working-agreement.md`.

---

## Naming

| Type | Pattern |
|------|---------|
| SPEC | `SPEC-NNN-short-title.md` under `specs/<area>/...` |
| Epic | `EPIC-NNN-short-title.md` |
| RFC | `RFC-NNN-short-title.md` |
| Decision | `YYYY-MM-DD-short-slug.md` in `docs/decisions/` |
