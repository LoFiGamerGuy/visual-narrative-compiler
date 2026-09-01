# ADR-0036: generated provider evidence is pinned by hash, not Git

- Status: accepted
- Date: 2026-09-01

## Context

The G07 bakeoff produced 16 raster candidates and 19 provider records, including an OpenAI pre-HTTP failure, a Gemini interaction recovered without a second generation, and a paid xAI output-transport failure. Committing generated rasters or raw runtime records would violate the safe-source rule, while leaving their existence and accounting dependent only on mutable local paths would make later comparison unauditable.

## Decision

Track a deterministic non-art manifest containing the exact SHA-256, byte count, request identity, execution state, cost, input/output hashes, failure tags, and pending-review state for every local provider record and candidate. Keep the underlying provider records and raster candidates ignored under `experiments/`.

The validator must decode every candidate, match every record and artifact byte hash, reconcile the 16 required-candidate charges plus paid failures, prove the Gemini failed/recovered records share one request and one generation charge, restrict BFL inputs to the two approved public-control hashes, and fail if Git tracks any path under `experiments/`.

## Consequences

- The manifest can detect loss or drift without making generated material source-controlled.
- Missing or corrupt bytes create a restoration gate; they do not authorize a rerender.
- A recovered interaction is not charged twice, while a paid no-candidate failure remains in aggregate spend.
- Hash integrity does not supply human review, visual acceptance, reproducibility, or commercial clearance.
- The current vault root is `e84b04029ca14b9a40dbdcd2e6d2937c322bf019df2191d032169e062696d3ab`.
