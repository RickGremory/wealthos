# ADR-003: Open-core licensing and product model

- **Status:** accepted
- **Date:** 2026-07-23
- **Deciders:** WealthOS core

## Context

WealthOS is positioned as a SaaS platform for independent professionals. We want community contribution and transparency without giving away the entire commercial product for free.

## Decision

Adopt an **open-core** model:

- **Core** (this repository and designated packages) remains open and self-hostable where documented
- **Commercial / cloud features** (hosted ops, advanced modules, support SLAs, etc.) may be proprietary or separately licensed

Exact license boundaries for proprietary modules will be documented as those modules appear.

## Consequences

### Positive
- Trust and contribution from builders who want to inspect core finance logic
- Clear path to a sustainable SaaS business
- Self-host option for users who need control

### Negative / trade-offs
- Must carefully separate open vs paid surfaces to avoid license ambiguity
- Feature gating and packaging add product complexity
- Community expectations must be managed explicitly in docs

## Alternatives considered
- Fully closed source — simpler commercially; weaker trust for money software
- Fully open / AGPL everything — maximum openness; harder commercial differentiation
- Source-available non-OSS — middle ground; often confuses contributors
