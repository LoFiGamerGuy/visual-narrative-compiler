# ADR-0039: human-review rollup preserves dimensions without composite ranking

- Status: accepted
- Date: 2026-09-01

## Context

Future G07 human judgments need to join exact cost, latency, raster drift, failure tags, and per-assertion results. An opaque weighted score could conceal failures or silently change the engineering route, while premature deblinding or fixture leakage could fabricate evidence.

## Decision

Compile arm rollups only from a complete, exact-packet, evidence-eligible timed session and the vault-derived deblinding mapping root. Preserve each automated diagnostic, assertion result, failure tag, and candidate/repeat decision separately. Do not compute a composite score, automatic rank, or automatic selection change.

While review is pending, publish only a gate record with measured nonhuman evidence and null human arm results. Validation fixtures may exercise the compiler but must remain explicitly synthetic and must fail the real-evidence path.

## Consequences

- Missing, reordered, fixture, or mapping-mismatched sessions cannot alter arm evidence.
- Review outcomes remain inspectable by dimension rather than collapsed into an unreviewable number.
- Any later change to ADR-0025's hardening route requires a new evidence-citing ADR.
- Current real review state remains 0/20 decisions, null minutes, zero accepted candidates, and no human arm results.
