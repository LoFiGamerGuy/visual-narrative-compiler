# ADR-0005: Actor assets must be pose- and prop-separable

## Status

Accepted from the 2026-08-31 actor-matte G07 control.

## Evidence

The deterministic actor-matte composites left more than 91% of the calibrated table plate unchanged and preserved left/right role assignment. Both nevertheless failed the frozen seated-at-table assertion because the only locally available adult actor plates contain their own furniture and incompatible body poses.

## Decision

Do not treat existing full-frame character renders as reusable controllable actor assets. A future asset registry needs pose, wardrobe, prop, alpha/matte, camera, and source-provenance records independently addressable from the character identity label.

## Consequences

The immediate next local foundation is a minimal source-of-truth asset/canon/panel-plan record set for known CH01 material. New actor-asset generation or model training remains a separate renderer/asset experiment and must not be smuggled into the control path.
