# Security Policy

## Supported versions

WealthOS is pre-release / scaffold. Security fixes apply to `main` until versioned releases exist.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security reports.

Instead, contact the maintainers privately (GitHub Security Advisories preferred when enabled on the repository, or a private message to `@RickGremory`).

Include:

- Description of the issue
- Steps to reproduce
- Impact (data exposure, auth bypass, org isolation failure, etc.)
- Any suggested fix (optional)

## What to expect

- Acknowledgement when the report is received
- Status updates while we investigate
- Credit in release notes if you want it (optional)

## Domain-sensitive areas

Highest priority:

- Cross-Organization data access
- Auth / session handling
- Transaction integrity and silent balance mutation
- Secrets in logs, clients, or the repository
