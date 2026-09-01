# ADR-0074: safe-source r3 pins the release-r3 boundary

- Status: accepted
- Date: 2026-09-01

## Context

Safe-source r2 predates the current handoff, exhaustive prerequisite lattice, and release gate r3. The final tracked boundary needs a fresh non-self-referential source inventory while unrelated workspace material remains untracked.

## Decision

Issue safe-source r3 against already-pushed commit `00498df557e56889ce161095572fcf1d09d95498`. Preserve r2 by exact hash and reuse the same path/data exclusions.

## Consequences

- R3 inventories 412 paths / 8,791,840 bytes at tree `3052f539…cc6d1` and inventory root `a3a0c65c…3e618`.
- Exactly two approved public controls and zero generated-experiment, prohibited-extension, or over-10-MiB paths are tracked.
- Thirteen/thirteen supersession, rewrite, commit/tree/inventory/blob/exclusion mutations fail.
- Current tracked scope and origin parity validate; unrelated local assets, launchers, generators, and trainers remain untouched and outside Git.
- Source integrity does not create generated-art retention, human review, authority, or production evidence.
