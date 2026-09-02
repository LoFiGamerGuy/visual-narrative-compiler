# ADR-0146: Owner hub r7 unifies final evidence without publishing art

Date: 2026-09-01

Status: Accepted

## Context

Hub r6 links art history and production capacity, but the current reproducer, safe-source capture, decision defaults, and release r10 were added later.

## Decision

Extend hub r6 with a five-link final-evidence layer and extend exact-link manifest r4 by five resources. Keep the hub ignored/local and track only builders, validators, hashes, and link metadata.

## Evidence

- Hub r7 links one prior HTML hub and four current text/JSON records.
- Its index and packet rebuild byte-identically; 17/17 mutations are rejected.
- Link manifest r5 preserves all 117 prior bindings and reaches 122 resources: 109 ignored local and 13 tracked metadata links.
- Link validation rejects 15/15 mutations.
- Decision, provider, upload, spend, acceptance, and executable state remains zero/null.

## Consequences

The owner has one current local entry point for all art/review history and final engineering evidence. Generated pixels remain ignored, unpublished, unaccepted, and commercially uncleared.
