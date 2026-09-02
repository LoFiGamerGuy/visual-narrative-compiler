# ADR-0151: Unavailable service fields remain null and commercial status open

Date: 2026-09-01

Status: Accepted

## Context

The final handoff must not infer a model, endpoint, cost, reproducibility, license grant, or commercial status from built-in ImageGen results that did not expose those fields.

## Decision

Reconcile all 29 RenderRecords against the continuity profile, exact authorized hashes, non-canon boundary, model/license registry, and closeout. Preserve all unavailable service fields as null with `unavailable_not_zero: true` and keep commercial/exact-base status open.

## Evidence

- 29 records = 26 CH05 + three non-canon, with 29 exact prompts/outputs and 39 reference uses.
- Exactly three authorized hashes match local files; no other hash appears.
- Model, endpoint, request ID, usage, cost, and seed are null in all 29 under the exact unavailable contract.
- All 29 are pending review; zero are accepted, commercially cleared, or reproducible.
- No real/adult likeness, child-related material, private reference, LoRA, dataset, BFL upload, or other-provider upload is recorded.
- Twenty-four/twenty-four mutations are rejected.

## Consequences

The built-in route remains provenance-limited fictional research. `$0` describes paid API/cloud activity only; built-in monetary cost remains unavailable. No license, rights, exact-base, or canon conclusion is inferred.
