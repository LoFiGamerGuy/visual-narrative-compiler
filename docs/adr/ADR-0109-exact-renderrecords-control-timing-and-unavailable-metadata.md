# ADR-0109: Exact RenderRecords control timing and unavailable metadata

Date: 2026-09-01

Status: Accepted

## Context

The 29 built-in ImageGen candidates span 26 CH05 records and three separately non-canon future-LitRPG concepts. Their source evidence contains exact prompt, reference, output, dimensions, elapsed-time, review-state, and candidate-file data. The built-in product does not expose model, endpoint, request ID, provider usage, monetary cost, or seed.

Earlier narrative summaries reported 155.766 seconds for the three concept candidates and 1,385.824 seconds for all 29 candidates. Exact candidate and batch records sum to 154.978 and 1,385.036 seconds respectively, a 0.788-second difference.

## Decision

1. Treat exact per-candidate records and their batch summaries as authoritative for timing and reference-use reconciliation.
2. Preserve prior validator output and release evidence as historical evidence. Record the 0.788-second correction append-only instead of rewriting source evidence or release gates.
3. Represent unavailable model, endpoint, request ID, usage, cost, and seed fields as explicit `null`, never as zero, an inferred value, or a provider claim.
4. Keep all 29 candidates pending human review and unaccepted. The audit does not promote generated pixels or establish commercial clearance.

## Evidence

- `production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json`
- `docs/research/evidence/ch05-renderrecord-completeness-audit-r1.json`
- `docs/research/evidence/future-litrpg-concept-timing-reconciliation-r1.json`
- 29 exact candidate records, 39 reference uses, and 1,385.036 observed seconds.
- All 29 prompts, outputs, dimensions, elapsed times, candidate paths, hashes, review states, and input-reference hashes validate.
- Six unavailable service fields are explicit `null` in all 29 records.
- The completeness audit rejects 27/27 mutations; the timing reconciliation rejects 12/12 mutations.

## Consequences

- Exact observed time is suitable for engineering envelopes but is not a cost, SLA, provider throughput claim, or reproducibility guarantee.
- Missing built-in metadata remains a measurable limitation of this route.
- Historical 155.766/1,385.824-second text must be read with this correction; historical evidence remains byte-preserved.
