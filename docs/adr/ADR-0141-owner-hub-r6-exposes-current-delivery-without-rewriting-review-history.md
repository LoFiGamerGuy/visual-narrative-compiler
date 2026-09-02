# ADR-0141: Owner hub r6 exposes current delivery without rewriting review history

Date: 2026-09-01

Status: Accepted

## Context

Hub r5 exposes the production pilot and lifecycle evidence but predates chapter duration capacity, the operating playbook, and delivery bundle r2. Those resources should be reachable without altering prior local packets or the 112-link r3 manifest.

## Decision

Create append-only hub r6 over r5 and exact-link manifest r4 over r3. Add the capacity chart, playbook, delivery summary, and exact bundle. Preserve generated images as ignored local artifacts and track only hashes, metadata, documentation, builders, and validators.

## Evidence

- Hub r6 has five links: one prior HTML hub, one image, and three text/JSON resources; its two generated local artifacts rebuild byte-identically.
- Hub validation rejects 17/17 mutations.
- Link manifest r4 preserves all 112 prior bindings and adds five resources for 117 total: 108 ignored local and nine tracked metadata links.
- Link validation rejects 15/15 mutations.
- Cost ledger r27 accounts for duration, playbook, delivery r2, and hub/link work as four additional zero-external-cost milestones, reaching 68 with zero requests, uploads, or paid cost.

## Consequences

The current review entry point contains both art-review history and production-engineering evidence. Link inclusion remains distinct from acceptance, execution, publication, commercial clearance, or exact-base selection.
