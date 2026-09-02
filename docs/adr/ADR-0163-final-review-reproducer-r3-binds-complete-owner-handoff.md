# ADR-0163: Final review reproducer r3 binds complete owner handoff

Date: 2026-09-01

Status: Accepted

## Context

Release r12 proves the review-contract extensions, but hub r9/link r7 and the candidate worksheet were added later. A compact final command set is needed to reproduce both engineering integrity and the exact owner-facing surface.

## Decision

Run ten local/no-network domains: release r12, safe-source r4, closeout r3, handoff consistency, candidate worksheet, hub r9, link r7, frozen/baseline integrity, tracked-source scope, and current remote parity. Normalize only two live decimal tracked-path diagnostics; bind every script and normalized stdout hash.

## Evidence

- Ten/ten domains pass in 166.588 seconds.
- Independent replay passes and rejects 29/29 state, denominator, result, activity, planning, and normalization mutations.
- Current state: 29 candidates, 50 plans, 12 batches, 134 links, 67 priority links, 112 worksheet checks, release 84, source 934, cost 82, frozen 16 + baseline 4.
- Provider calls/uploads/ingestion/acceptance/clearance/execution/spend remain zero; human minutes remain null.
- Current `main` and `origin/main` are exact at replay.

## Consequences

One command now reproduces the complete final review handoff without reinterpreting historical evidence. Passing still grants no upload, generation, owner ingestion, acceptance, rights, exact-base, or production authority.
