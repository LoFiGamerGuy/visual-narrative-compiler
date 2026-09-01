# ADR-0083: final safe-source release pins the pushed r5 boundary

- Status: accepted
- Date: 2026-09-01

## Context

Safe-source r3 predates the complete evidence lineage, release r5, provider chronology, and autonomous closeout. The final handoff needs a non-self-referential inventory of the already-pushed r5 boundary while unrelated workspace material remains excluded.

## Decision

Issue safe-source r4 against pushed commit `f1803bddcaea1906b79aa3520e72036ada1b7354`. Preserve r3 by exact hash, retain its explicit exclusions, and require the current branch to equal `origin/main` when the validator closes.

## Consequences

- R4 inventories 459 paths / 9,234,040 bytes at tree `aaab99df…35e0c` and inventory root `1ce5104c…b41e6`.
- Exactly two approved public controls and zero generated-experiment, prohibited-extension, or over-10-MiB paths are tracked.
- Thirteen/thirteen supersession, rewrite, commit/tree/inventory/blob/exclusion mutations fail.
- Untracked imported assets, launchers, generators, and trainers remain untouched and outside Git.
- The manifest proves source integrity and remote provenance only; it does not create review, authority, or production evidence.
