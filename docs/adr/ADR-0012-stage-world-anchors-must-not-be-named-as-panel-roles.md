# ADR-0012: Stage world anchors must not be named as panel roles

Date: 2026-09-01

## Context

The kitchen bootstrap OBJ labels its two seats `Anchor_SOREN_LEFT_SEATED` and `Anchor_SIGRID_RIGHT_SEATED`. Under the imported Blender diagnostic camera, world X-negative appears screen-right and world X-positive appears screen-left. Frozen G07 semantics describe left/right in the panel layout, not an undocumented world coordinate direction.

Using those labels directly as G07 renderer controls would silently invert screen-side role assertions or force role identity into a shared set asset. That conflicts with both role-binding measurement and the shared-asset boundary.

## Decision

Treat the r1 character-named anchor labels as a legacy/bootstrap limitation, not semantic role authority. Do not feed `kitchen-table-blender-control-bundle-v1` into a frozen-case renderer test. The next stage revision must use neutral world-coordinate anchors and a separate, explicit world-to-comic-panel projection mapping. A `ComicPanelPlan` assigns roles to those neutral anchors; an `AnimationShotPlan` will have its own mapping later.

## Consequences

The r1 bundle remains useful for Blender execution and deterministic construction checks, but is not Stage-A-compatible. No frozen gauntlet content changed. This correction prevents a visually plausible but semantically inverted role-binding result.
