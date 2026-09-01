# ADR-0069: safe-source r2 pins the latest pushed authority frontier

- Status: accepted
- Date: 2026-09-01

## Context

Safe-source r1 predates the release gate, selector compatibility proof, and authority frontier. A source manifest cannot safely contain its own commit, and the workspace also contains unrelated untracked imported assets, launchers, generators, and trainer material.

## Decision

Issue append-only safe-source release r2 against already-pushed commit `43fc787f783236c1c5dae9f4694a6e2a804e0aae`. Pin every blob and its Git and SHA-256 identities, preserve r1 by exact hash, and explicitly exclude both the established prohibited classes and unrelated untracked workspace material.

## Consequences

- R2 inventories 387 paths / 8,535,516 bytes at tree `4e85a8c3…5f70b` and inventory root `53af7d04…13d6b`.
- The manifest contains exactly two approved public controls and zero generated-experiment, prohibited-extension, or over-10-MiB paths.
- Thirteen/thirteen supersession, rewrite, commit/tree/inventory/blob/exclusion mutations fail.
- Current tracked scope and origin/main parity validate; unrelated untracked workspace files remain untouched and outside the release.
- This is source/evidence integrity only, not generated-art retention, review, commercial clearance, or production authority.
