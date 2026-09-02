# ADR-0125: Delivery bundle pins measured output without promotion

Date: 2026-09-01

Status: Accepted

## Context

The overnight work now spans generated candidates, chapter planning, deterministic review artifacts, route evidence, owner decisions, and seven append-only release gates. A single exact handoff record is needed without converting engineering selections into owner acceptance.

## Decision

Compile an append-only delivery bundle at the release-r7 base commit. Bind exact input and strongest-candidate hashes, direct review paths, counts, measured time, remaining decisions, limitations, and activity fields. Keep owner decisions, acceptance, commercial clearance, executable panels, plan revisions, human minutes, paid calls, and paid spend at zero or null.

## Evidence

- 29 candidates bind: 26 CH05 and three separately labeled non-canon concepts.
- Fourteen CH05 plans have candidates; all 50 plans appear in 12 coherent 3–5-panel production batches.
- Fourteen strongest engineering candidates and 105 review resources have exact path/hash bindings.
- Observed generation time is 1,385.036 seconds across 39 reference uses; paid API/cloud spend is $0 and built-in monetary cost is unavailable.
- Ten owner decisions remain unresolved and eight limitations are explicit.
- The delivery validator rejects 21/21 state, denominator, timing, cost, decision, acceptance, and planning-boundary mutations.

## Consequences

The bundle is the current engineering handoff, not art acceptance, commercial clearance, an exact production-base declaration, or completion of the time-bounded overnight goal. Its changed-file inventory intentionally ends at the release-r7 base commit so the handoff remains append-only.
