# Contributing to WealthOS

Thanks for helping build the financial operating system for independent professionals.

## Before you start

1. Read the [README](../README.md)
2. Skim `.ai/project.md` (mission, stack, domain invariants)
3. Review relevant docs under `docs/` and ADRs under `docs/adr/`

## Development setup

Setup commands will land with the Phase 1 skeleton (`backend/` + `frontend/`). Until then:

- Copy `.env.example` → `.env` when services exist
- Prefer `docker compose` for local dependencies

## How to contribute

1. Open an issue (or use an existing one) for non-trivial work
2. Branch from `main` using the naming in `docs/engineering/09-git-workflow.md`
3. Keep PRs small and reviewable
4. Fill out `.github/PULL_REQUEST_TEMPLATE.md`
5. Ensure Organization scoping, UUID, and UTC rules are respected for money-related changes

## Coding standards

See `docs/engineering/08-coding-standards.md` and `.ai/coding-style.md`.

## Security

Do not report vulnerabilities in public issues. See [SECURITY.md](./SECURITY.md).

## License

Contributions are under the repository [LICENSE](../LICENSE), within the open-core model described in [ADR-003](../docs/adr/ADR-003-open-core.md).
