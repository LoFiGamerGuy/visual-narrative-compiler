# ADR-0040: use 16px inward cosine feather for the next local repair-mechanics test

- Status: accepted
- Date: 2026-09-01

## Context

The selected OpenAI G07 target candidate can be restricted by deterministic compositing, but the r1 hard rectangular mask introduces a visible boundary discontinuity. Boundary smoothing must retain exact exterior protection and must not be selected by visual appeal alone.

## Decision

For the next local-only repair-mechanics test, use the narrowest inward cosine feather satisfying the predeclared rule: at least 90% reduction in artificial cross-boundary jump versus the hard mask, at least 99% of the hard-mask central green signal, zero changed pixels outside support, and zero P036 lettering-safe-zone overlap.

Seven variants were measured at 0, 2, 4, 8, 16, 24, and 32 pixels. Only the 16-pixel variant qualifies, with 91.2633518% artificial-jump reduction, 99.461535% central green-dominant pixels, zero exterior change, and zero lettering overlap.

## Consequences

- The policy selects compositor mechanics, not a provider output or finished panel.
- The unaccepted G07 proxy remains research evidence; no human art review has occurred.
- Inward feathering preserves exact exterior bytes but reduces the fully replaced area near the boundary.
- Rectangular proxy results do not establish performance on hands, hair, faces, line art, props, irregular masks, or CH05 continuity.
- Narrative applicability requires a separate mask-topology check before any production proposal.
