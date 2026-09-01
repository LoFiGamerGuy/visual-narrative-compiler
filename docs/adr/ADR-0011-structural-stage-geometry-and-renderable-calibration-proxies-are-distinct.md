# ADR-0011: Structural stage geometry and renderable calibration proxies are distinct

Date: 2026-09-01

## Context

`kitchen-table-stage-v1.obj` is a portable, named spatial contract: floor, wall, table, anchors, and a camera line. Its zero-thickness planes and line-like anchors import correctly in Blender, but are not reliable visible render primitives. The first Workbench calibration image therefore could not expose the seating contract for review.

## Decision

Keep the pinned OBJ/`.blend` as the structural shared-stage authority. For deterministic visual inspection, derive separately versioned, plainly colored solid proxy primitives from the same coordinates. Record their script and output hashes. Do not replace the structural asset with the proxy and do not call the proxy final art, a character asset, a camera match, or grounded panel evidence.

## Consequences

The r4 wide diagnostic proves that Blender can render the table and both seating positions from the contract. It does not prove artistic occlusion, character identity, role binding, legacy composition, or set readiness. A future renderer adapter needs explicit, versioned control assets and its own calibration record.
