# ADR-0094: Measure density per panel, not from style labels

- Status: accepted
- Date: 2026-09-01

## Context

Phone-footprint measurements across the selected 14 show that style labels do not reliably predict density. c014's `limited_ink_flat` panel has 0.275889 edge occupancy and the highest measured colorfulness, while calm c013/c015 panels measure 0.091168/0.096065. c014→c015 is the largest adjacent appearance-feature jump at 5.6517. c005 remains the highest selected edge-occupancy panel at 0.308471.

Across all 26 CH05 candidates, all-six-dimension engineering passes are 5/6 cel-painted, 5/8 clear-line watercolor, 4/6 limited ink, and 3/6 clean graphic. Tasks and reference conditions are unbalanced, so these counts cannot be generalized as universal style scores.

## Decision

Retain the role-aware cel-painted/clear-line route. Use cel-painted treatment for character/emotion/hero anchors and clear-line staging for causal action/transitions, subject to exact panel review. Do not assume `limited_ink_flat` is low-density or choose clean graphic/limited ink as a uniform chapter treatment from these counts.

Measure density on each rendered panel at its intended phone footprint. Treat c014's dense action punctuation and c005's foliage density as explicit owner decisions. If rejected, target only the exact density failure rather than rerolling the sequence broadly.

## Consequences

- Style names remain creative directions, not quantitative guarantees.
- c014→c015 may be retained as deliberate action-to-calm rhythm or rejected as finish discontinuity by the owner.
- Global features remain diagnostic only; manual review is authoritative for hair, wardrobe, identity, hands, objects, causality, and acceptance.
- No style, candidate, sequence, or production base is accepted or commercially cleared.
