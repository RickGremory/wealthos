# ADR-012

# Organization is the Tenant Boundary

**Status:** Accepted

**Date:** 2026-07-23

---

## Context

Tenant isolation is one of the most critical architectural decisions in any SaaS application.

Changing the tenant boundary after implementation is expensive and risky.

---

## Decision

The Organization is the tenant boundary across the entire platform.

Every request is executed within the context of an Organization.

---

## Rationale

Organizations represent the real-world entity that owns financial information.

Examples include:

- Independent professionals
- Small businesses
- Families
- Agencies
- Consulting firms

---

## Consequences

All repositories must filter by organization.

APIs must validate organization access.

Services must operate within an organization context.

---

## Benefits

- Strong tenant isolation.
- Better security.
- Easier horizontal scaling.
- Simpler authorization model.

---

## Future Considerations

This decision enables enterprise features such as:

- Team management.
- Multiple organizations per user.
- Organization switching.
- Shared dashboards.
