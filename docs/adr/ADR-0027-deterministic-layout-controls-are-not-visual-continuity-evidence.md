# ADR-0027: deterministic layout controls are not visual-continuity evidence

- Status: accepted
- Date: 2026-09-01

## Context

Before approved base art exists, deterministic geometry can exercise chapter compiler contracts cheaply: stable panel linkage, role count, lettering exclusion, causal object dependencies, output hashing, and packet assembly. The same controls cannot demonstrate character identity, acting, style, anatomy, material continuity, seam quality, or narrative-panel acceptance.

## Decision

Record deterministic layout sequences as `ComicPanelSequenceLayoutControl`, never `RenderRecord` or approved base raster. Pin source and output hashes, state exact compiler assertions, keep human-review minutes null, and mark every output not art/not provider input. Continuity tokens may prove dependency plumbing only; they cannot satisfy visual-continuity or panel-acceptance gates.

The P033–P038 control uses only existing `ComicPanelPlan` intent and control-local geometry/color conventions. It adds no canon or directing intent. `AnimationShotPlan / E-Conte` remains null and separate.

## Consequences

- Passing controls can unblock compiler/run-ledger work without external spend.
- They do not reduce the count of missing approved bases or accepted panels.
- A later art route must repeat continuity and assertion review on actual immutable rasters.
- Any attempt to promote a layout-control raster through the comic input gate requires a distinct authorized human approval record; the control manifest itself grants none.
