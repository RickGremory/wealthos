# Identity

Users who can belong to one or more Organizations.

## Purpose

Own the `User` aggregate and bootstrap identity before authentication.

## Public API

| Method | Path | Notes |
|--------|------|--------|
| `POST` | `/api/v1/identity/users` | Dev/bootstrap create user |
| `GET` | `/api/v1/identity/health` | module probe |

Authentication (passwords, OAuth, sessions) is intentionally out of scope for now.
