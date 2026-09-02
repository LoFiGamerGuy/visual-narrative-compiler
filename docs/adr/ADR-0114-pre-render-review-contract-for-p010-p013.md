# ADR-0114: Pre-render review contract for P010–P013

Date: 2026-09-01

Status: Accepted as a dry-run contract

## Context

The P010–P013 production manifest predeclares five review artifacts, but a packet can still become misleading if its candidate checks, failure vocabulary, repair semantics, and promotion rules are improvised after images arrive.

## Decision

Bind review semantics before rendering. Each of four candidate slots receives 11 required checks: cast count, role identity/order, hair, wardrobe, mature anatomy, hands/story object, causal action/clue, lettering clearance, phone readability, density role, and sequence finish continuity. Predeclare 11 failure classes, five review artifacts, five promotion rules, and two one-class repair slots.

## Evidence

- Four candidate slots × 11 empty checks.
- Five artifacts remain `NOT_BUILT` with null path/hash/dimensions.
- Eleven exact failure classes and five explicit promotion rules.
- Sequence continuity, cadence, lettering, reviewer, minutes, and decision fields remain null.
- 17/17 malformed denominator/activity/planning mutations are rejected.

## Consequences

- Failures must be preserved and classified; warnings cannot be silently promoted.
- A repair may change only one failure class and must preserve passing rows.
- Engineering review cannot establish commercial clearance or exact production-base eligibility.
- No pixels, review events, decisions, repairs, provider activity, or acceptance are created by this contract.
