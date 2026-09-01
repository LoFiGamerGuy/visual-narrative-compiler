# ADR-0073: release gate r3 pins the current handoff and authority lattice

- Status: accepted
- Date: 2026-09-01

## Context

Release gate r2 predates the latest selected-route handoff and exhaustive P036 prerequisite lattice. Both materially improve the integrity of the handoff boundary but do not change renderer measurements or grant authority.

## Decision

Issue release gate r3 with r2 as an immutable 60-check base. Append five checks: handoff r2, prerequisite lattice r1, and production cost ledgers r10-r12. Record the current blocked state directly in the gate.

## Consequences

- R3 passes 65/65 checks and rejects 16/16 supersession/base/extension/boundary/activity mutations.
- Observed local runtime is 80.178 seconds: 79.806 seconds for r2 and 0.371 seconds for the five extensions.
- G07 remains 0/20 decisions; CH05 retains zero approved inputs/cap/RenderRecords/acceptances and P036 retains four root/nine total blockers.
- `next_external_action` remains null; no network request, provider call, upload, download, or external cost occurs.
- The nested revisions preserve historical check counts and evidence semantics instead of expanding prior gates in place.
