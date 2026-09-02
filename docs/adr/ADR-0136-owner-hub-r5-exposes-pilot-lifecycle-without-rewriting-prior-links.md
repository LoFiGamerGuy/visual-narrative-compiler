# ADR-0136: Owner hub r5 exposes pilot lifecycle without rewriting prior links

Date: 2026-09-01

Status: Accepted

## Context

The current owner hub predates the six-root unlock, prompt drafts, pre-render packet, guarded lifecycle, and chapter lifecycle map.

## Decision

Extend immutable hub r4 with seven direct resources and extend the exact 105-link manifest r2 with those same pilot/lifecycle resources. Preserve every earlier path/hash/category binding. Keep the hub local, offline, ignored, and read-only.

## Evidence

- Hub r5 has seven links: one image, one prior HTML hub, and five tracked text/JSON records.
- Consecutive builds produce identical index, packet, and thumbnail hashes.
- Sixteen/sixteen hub mutations are rejected.
- Link manifest r3 contains 112 exact resources: 105 prior plus seven new.
- Git state is 106 ignored local and six tracked metadata links; 15/15 link-manifest mutations are rejected.
- No decision, acceptance, execution, provider, upload, cost, or human-minute state is created.

## Consequences

R5 is the current local owner entry point and r3 is the exhaustive current link inventory. Earlier hubs and manifests remain immutable.
