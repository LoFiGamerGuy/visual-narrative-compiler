# ADR-0129: Final reproducer matrix separates live diagnostics from pinned evidence

Date: 2026-09-01

Status: Accepted

## Context

The current handoff depends on integrated release, delivery, source, frozen-target, cost, and Git-lineage evidence. Running only the nested release gate would not independently expose failures in all domains.

## Decision

Run seven explicit local domains and bind script hashes, arguments, raw and normalized stdout hashes, elapsed times, immutable inputs, base commit, and compile-time remote parity. Permit `TRACKED_COUNT_ONLY` normalization only for the safe-source capture and current tracked-scope commands.

## Evidence

- Seven/seven domains pass in 47.129 observed seconds.
- Release r8 compatibility represents 49 effective checks.
- Delivery binds 29 candidates, 50 plans, and 105 review links.
- Source capture binds 735 paths; frozen integrity binds 16 gauntlet plus four baseline paths.
- Cost ledger r25 binds 54 zero-external-cost milestones.
- Remote lineage validates branch/origin configuration, ancestry, and clean tracked tree/index while excluding unrelated untracked material.
- Twenty/twenty matrix mutations are rejected.

## Consequences

The matrix is the compact current engineering reproducer. It does not replace the underlying evidence, normalize captured inventory or semantic state, ingest review, or promote art.
