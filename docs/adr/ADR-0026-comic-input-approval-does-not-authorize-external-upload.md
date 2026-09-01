# ADR-0026: comic input approval does not authorize external upload

- Status: accepted
- Date: 2026-09-01

## Context

A chapter-scale repair pipeline needs approved base rasters and masks, but local art approval, local repair eligibility, and permission to upload an exact input package to an exact provider are different decisions. Treating any one as the others would silently expand the data boundary and make a missing record look like consent.

## Decision

Use separate `ComicPanelBaseRasterApproval` and `ComicPanelRepairMaskReview` records. Both require exact panel/revision linkage, file hashes, applicable semantics, authorized timed human review, and explicit local permission. External execution additionally requires `external_upload_authorized=true` plus exact provider, model snapshot, and endpoint fields.

The compiler gate in `src/north_garden/comic_input_gate.py` fails closed. Template/missing/pending records are never executable. Hash-valid files must also decode as supported raster formats with declared dimensions; masks must be grayscale PNGs with valid nonzero fractions, zero declared lettering-safe-zone overlap, target/protected semantics, and seam review. No `ComicPanelPlan` or local approval record implies an external upload.

For external execution, self-declared provider fields are insufficient. The caller must separately supply the exact authorized provider/model/endpoint scope and it must match the reviewed records. An absent or mismatched authority scope is a hard failure.

## Consequences

- The current CH05 P033–P038 demonstration slice remains local preflight only.
- The P036 smoke raster remains unaccepted and cannot become a base raster implicitly.
- A future exact upload request is an explicit authority gate even after local human approval.
- These are comic records; `AnimationShotPlan / E-Conte` remains null and separate.
