# ADR-0050: repair outcome evidence is state-specific and append-only

- Status: accepted
- Date: 2026-09-01

## Context

The v2.0 RenderRecord proves provider, journal, input/output, timing, usage, cost, and review completeness, but predates the scale-aware boundary selector. Adding optional fields to it would let completed repairs omit the exact width/topology/visual/review chain and could let an unknown provider outcome imply evidence that does not exist.

## Decision

Keep v2.0 unchanged. Add the v2.1 `comic_targeted_repair_v2` profile as an append-only contract.

A completed repair must bind the exact selector contract, panel/revision profile and local width, support and inward-alpha bytes, topology record, exact base/candidate visual-boundary evidence, exact-zero exterior result, no-change result, and an identified timed seam-review decision. An explicit provider failure binds only the selector/profile/support/alpha/topology inputs and declares that no candidate outcome exists. An outcome-unknown incident uses schema 1.1 and contains none of the boundary-outcome fields.

## Consequences

- Topology evidence cannot masquerade as exact-base visual evidence or seam acceptance.
- Failed and unknown calls cannot fabricate candidate-derived measurements.
- The seam decision is narrower than full candidate acceptance; the ordinary RenderRecord review remains pending until its separate human review completes.
- Synthetic completed/failure/unknown fixtures validate, and 15/15 selector, width, hash, visual, exterior, no-change, timing, failure, and unknown-outcome mutations fail.
- Real CH05 RenderRecords, candidates, seam reviews, requests, uploads, and production spend remain zero.
