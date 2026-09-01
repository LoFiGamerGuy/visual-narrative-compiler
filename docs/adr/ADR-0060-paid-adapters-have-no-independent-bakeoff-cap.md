# ADR-0060: paid adapters have no independent bakeoff cap

- Status: accepted
- Date: 2026-09-01

## Context

The completed bakeoff ledger is aggregate, but later adapter edits could accidentally introduce a local `$100` interpretation, submit before reservation, or retry a recovery as a new reservation.

## Decision

Audit every paid adapter statically and through its no-network preflight. Require the shared cap environment and budget functions, exact adapter identity in the reserve call, reservation before the paid submission, and no adapter-local cap literal. Treat Gemini recovery as retrieval under the original held reservation. Keep BFL's pre-reservation public URL fetch limited to hash verification of its two approved controls.

## Consequences

- Four/four adapters reserve from the shared ledger before paid submission and have no local-cap path.
- The final ledger reconciles 18 entries: 17 committed, one proven-unsubmitted release, zero held; $1.057377 committed and $98.942623 available.
- Required candidates cost $0.987377; the additional xAI paid failure cost $0.07.
- BFL remains limited to the two public control keys/hashes and gains no expanded upload authority.
- Ten/ten cap, adapter, ordering, ledger, BFL, child-boundary, and activity mutations fail.
