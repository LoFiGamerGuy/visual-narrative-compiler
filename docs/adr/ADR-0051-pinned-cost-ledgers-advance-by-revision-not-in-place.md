# ADR-0051: pinned cost ledgers advance by revision, not in place

- Status: accepted
- Date: 2026-09-01

## Context

P036 readiness r2 pins the exact CH05 production cost-ledger r1 bytes. Adding later zero-cost milestones to r1 would invalidate that evidence chain even though committed and held cost remain zero.

## Decision

Restore and preserve r1 exactly. Record later milestones in append-only `ng-ch05-production-cost-ledger-r2`, which pins r1 by path and SHA-256 and declares that the prior record was not rewritten.

## Consequences

- Historical readiness records remain reproducible.
- R2 contains 18 unique local zero-external-cost milestones, an empty reservation-entry list, zero requests/uploads, $0 committed, $0 held, and no cap or availability.
- Eight/eight supersession, rewrite, authority, cap, cost, reservation, request, and count mutations fail.
- G07's unused capacity remains prohibited from funding CH05 production.
