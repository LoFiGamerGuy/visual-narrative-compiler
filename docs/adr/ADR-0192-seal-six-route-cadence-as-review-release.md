# ADR-0192: Seal the six-route cadence as a review release

## Status

Accepted as an engineering release decision. Owner visual disposition, candidate acceptance, rights clearance, commercial clearance, and exact-production-base selection remain open.

## Context

The CH05 program now has six complete 50-plan routes, a sequence-constrained three-block cadence, two matched reference ablations, a boundary audit, a three-arm P005-to-P006 attribution control, and two owner-facing handoffs. These records span 300 aligned candidates and a 50-panel assembled reading draft, but none is owner-accepted or commercially cleared.

The integrated release record at `docs/research/evidence/ch05-six-route-cadence-integrated-release-r1.json` binds the clean pushed pre-release commit `97e0591b02209310a2ff94d3bc1ee336ce51ae06`. Its 16 domains passed in 31.918454 seconds, representing 14 mutation suites and 298/298 rejected upstream mutations. The companion record validator rejects 26/26 mutations.

An append-only release record necessarily precedes the commit that publishes that record and its validator. Requiring the live checkout to remain byte-identical to the pre-release commit would make successful publication invalidate the evidence.

## Decision

Treat the integrated record as immutable historical execution evidence. Its exact recorded commit, command outputs, script hashes, clean worktree, and remote parity remain pinned. On later replay, require every current local validator to pass with its expected self-test, require the recorded commit to be an ancestor of current `main`, and require current `main` to be clean and exactly equal to `origin/main` at the same approved remote.

Advance the CH05 cost ledger append-only to r35. The current revision adds eight local evidence milestones and nine exact source bindings, bringing the ledger to 117 local zero-external-cost milestones. It records zero new provider calls, uploads, generation calls, candidates, or paid spend and preserves all historical built-in activity and unavailable service metadata.

## Consequences

The selected cadence is reproducible as a review package without being promoted to production. Publication no longer creates a false negative in the historical release validator, while source divergence, rewritten evidence, failed current validators, dirty tracked state, or remote drift still fail closed.

This decision authorizes no new generation, upload, provider, spend, acceptance, rights, commercial-use, canon, or exact-base action.
