# ADR-0042: use 8px context padding for the abstract P036 causal-shape control

- Status: accepted
- Date: 2026-09-01

## Context

The 16-pixel inward compositor boundary passes a large rectangle but requires a control that exercises the approved P036 hand/plank/tin causal relationship. A mask too close to the drawn proxy shapes can split the fully replaced core; excessive padding weakens targeting.

## Decision

Construct deterministic plank, reach, hand, and tin feature masks from the existing abstract layout coordinates. Compare 0, 4, 8, 12, and 16 pixels of context padding with the fixed 16-pixel inward boundary. Select the narrowest padding with one connected support/core/nonzero-alpha component, at least 40% union core retention, at least 15% core retention for every labeled feature, rectangularity no greater than 0.50, and zero lettering overlap.

Eight pixels is the narrowest qualifying context: 42.1067208% union core; feature-core retention 45.4681% plank, 44.4705% reach, 48.6920% hand, and 38.3842% tin; one connected core; rectangularity 0.215863; zero exterior and lettering change.

## Consequences

- The local compositor mechanics now exercise concavity and a 42-pixel thin reach feature.
- The result still does not exercise holes or disconnected support components.
- The selected support/alpha are abstract compiler controls, not a base raster, approved repair mask, character art, or authorized provider input.
- Any production mask must be authored and reviewed against an approved panel-specific base and cannot inherit approval from this control.
