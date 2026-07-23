# Working agreement (agents & humans)

## Communication modes during build

When implementing a SPEC, separate clearly:

### Architect Notes

- Why a decision was taken
- Trade-offs and future impact
- Links to ADR / RFC / SPEC

### Implementation

- Exact files, commands, and code
- Checklist ticks on the SPEC
- Commits matching the SPEC Commit Plan

Do not mix unexplained “magic” code with architecture rationale — both should be present, labeled.

## Source of truth for a sprint

The open SPEC under `specs/` is the execution contract. Strategy docs (Vision, ADR, RFC) are not rewritten mid-sprint.
