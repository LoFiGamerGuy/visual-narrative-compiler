# ADR-0030: local base-candidate intake is not approval

- Status: accepted
- Date: 2026-09-01

## Context

The production compiler needs exact raster bytes before human classification and art review can occur. Hashing a file is mechanical; deciding that it contains permitted fictional material, is suitable panel art, or may be repaired/uploaded is human authority. Combining intake and approval would make the first local file scan an implicit consent decision.

## Decision

Create `ComicPanelBaseRasterCandidate` records that decode the raster, bind its exact SHA-256/dimensions to a stable `ComicPanelPlan`, and retain pending/null classification. Candidate permissions are always false and human minutes are null. The approval gate recognizes only a distinct `ComicPanelBaseRasterApproval` record with completed positive-minute review.

Candidate intake never copies or uploads the raster. Runtime candidate records remain under ignored `experiments/intake`; tracked evidence contains only schemas, validators, and aggregate results.

## Consequences

- Six deterministic layout controls can exercise intake and hash matching but remain rejected by the base-approval gate.
- Intake cannot turn compiler geometry, smoke art, or any other raster into accepted art.
- Local repair and external upload remain separate later decisions under ADR-0026.
