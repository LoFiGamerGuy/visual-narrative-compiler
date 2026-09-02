# ADR-0135: Chapter batches reuse contracts but never evidence identities

Date: 2026-09-01

Status: Accepted

## Context

The guarded lifecycle was defined for seq03. Applying it chapter-wide risks either duplicating all tooling or reusing batch-specific evidence incorrectly.

## Decision

Reuse seven contract classes across all 12 batches: lifecycle schema, review checks, failure vocabulary, bounded repair, RenderRecord fields, live timer, and ignored packet builder. Rebind eight evidence classes for every batch: exact plans, owner roots, prompt hashes, references, RenderRecords/outputs, packet measurements, human reviews, and rights/exact-base decisions.

## Evidence

- All 50 plans appear once across 12 narrative-order batches.
- Seq03 alone is `DRAFT_BLUEPRINTED`; 11 batches have not entered the lifecycle.
- Production waves remain 1/2/5/4 and are not mistaken for narrative order.
- Forty-nine review artifacts are planned: 48 baseline batch artifacts plus the pilot density artifact.
- The 1900×1480 lifecycle map builds byte-identically and passed visual inspection.
- Twenty-two/twenty-two mutations are rejected.

## Consequences

The lifecycle can scale without copying evidence identities between scenes. No batch gains prompt, render, acceptance, or execution state.
