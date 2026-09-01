# ADR-0057: reproducibility claims require bounded exact artifact inventories

- Status: accepted
- Date: 2026-09-01

## Context

The selected route generates many ignored local artifacts. Claiming that “the pipeline is reproducible” from a few hand-picked hashes would hide changing files, while including timestamps, performance samples, provider output, or human review would manufacture determinism by normalization.

## Decision

Define eight exact local artifact groups and rebuild them twice through the same validators under the pinned instrumentation profile. Compare the complete sorted path/byte-count/SHA-256 inventory and its canonical root. Explicitly exclude nondeterministic record classes rather than rewriting or normalizing them.

## Consequences

- Twenty-six artifacts across eight groups and 4,862,061 bytes rebuild byte-identically with root `0a04832b…d3f3b18` on both passes.
- Eight/eight command, inventory, root, byte-identity, exclusion, and activity mutations fail.
- Suite timestamps/timings, provider candidates/responses, human decisions/minutes, and external runtimes remain outside the claim.
- This is exact reproducibility on the measured Windows/CPython profile, not cross-platform PNG identity, provider reproducibility, visual quality, or acceptance.
