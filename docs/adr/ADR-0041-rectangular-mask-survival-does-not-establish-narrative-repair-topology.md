# ADR-0041: rectangular mask survival does not establish narrative repair topology

- Status: accepted
- Date: 2026-09-01

## Context

ADR-0040 selects a 16-pixel inward cosine feather on a rectangular G07 proxy. The existing P036 abstract target-context mask was described as a causal repair region, but byte inspection shows it is also one fully filled axis-aligned rectangle. Applying the selected policy to it can test erosion and exterior mechanics, not irregular object boundaries.

## Decision

Record rectangle compatibility and irregular-topology sufficiency separately. The 16-pixel policy retains 79.0324089% of the P036 rectangle as a fully replaced core, preserves its one component, and changes zero pixels outside support or inside the lettering-safe zone.

Do not treat that result as evidence for concavities, holes, multiple components, or thin hand/plank/tin features. Require a deterministic causal-shape proxy before extending the compositor policy to narrative-mask applicability.

## Consequences

- The boundary policy remains mechanically viable for a large rectangle.
- The current abstract mask does not justify an irregular or object-aware repair claim.
- The next control may use only deterministic abstract geometry tied to the ComicPanelPlan; it remains non-art and unauthorized for upload.
- No provider-route, art-acceptance, character-continuity, or commercial conclusion changes.
