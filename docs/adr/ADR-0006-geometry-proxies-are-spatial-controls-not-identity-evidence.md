# ADR-0006: Geometry proxies are spatial controls, not identity evidence

## Decision

Use a local, non-biometric geometry-only proxy layer to validate deterministic role placement, common-table occlusion, non-contact blocking, and no-change controls before attributing failures to an image renderer. Keep proxy role tokens explicitly distinct from recurring-character identity.

## Evidence

`geometry_proxy_g07_control` ran frozen-semantic references G07a and G07b without modifying the gauntlet. Both role swaps passed token placement, two-proxy count, 356-pixel separation, common-table occlusion, and bit-identical no-change controls. No model, network call, adult likeness, or child asset was used. Records: `experiments/records/geometry_proxy_g07_v1/*-r3.json`.

## Consequences

This is a useful spatial-reference and compositing-control baseline, not a renderer benchmark, character identity test, or canonical final-art set. A later renderer-facing bundle must map independently controlled, licensed assets and camera/stage controls to these geometry interfaces before it may be frozen.
