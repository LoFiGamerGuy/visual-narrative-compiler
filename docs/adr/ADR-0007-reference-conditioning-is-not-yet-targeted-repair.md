# ADR-0007: Reference conditioning is not yet targeted repair

## Decision

Keep FLUX.2 Klein reference conditioning as a separate semantic-edit research arm. Do not represent it as targeted repair, a no-change control, or a replacement for explicit masked/local repair until a case-specific control demonstrates constrained non-target preservation.

## Evidence

The local proxy edit `proxy_g07a_reference_edit` retained the two-token common-table kitchen composition and changed the requested right token from orange to green in 35.307 seconds. However, pixel comparison against its fictional proxy input found 83.58% changed pixels and a full-frame changed bounding box. The graph and immutable output are recorded in `experiments/workflows/flux2_klein_proxy_reference_edit_v1.json` and `experiments/results/flux2_klein_proxy_smoke_20260901.json`.

## Consequences

The next smallest FLUX experiment is a reference-conditioned no-change and narrow-change proxy control with multiple seeds, explicit changed/non-target measurements, and human-review fields. It remains non-scoring, proxy-only, and distinct from grounded frozen-semantic evidence. Existing `baseline_legacy` and sequential-inpaint results remain unchanged.
