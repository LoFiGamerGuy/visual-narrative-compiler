# ADR-0188: Use measured sequence-level cadence for the next CH05 review route

## Status

Accepted as a provisional engineering recommendation. It does not accept or promote any route, sequence, panel, or generated pixel.

## Context

The review-only semantic-pass hybrid reaches 49 PASS / 1 WARN / 0 FAIL, but its 33 adjacent route transitions make finish continuity difficult to judge and unsuitable as a chapter-production recommendation.

The six-route comparison in `docs/research/evidence/ch05-six-route-comparison-r1.json` (`c40d3a945704639855135cda4d011529f13c5c71d857b7807914823d7e248229`) compares 300 hash-bound candidates. Its deterministic sequence optimizer assigns exactly one route to each of the 11 existing ComicPanelPlan generation blocks and gives semantic/identity failure avoidance priority over route transitions, then warnings and secondary overall/lettering burden.

## Decision

Recommend this sequence-level cadence for owner review:

- S01 / P001–P005: reduced-palette text-only control;
- S02–S08 / P006–P039: R6;
- S09–S11 / P040–P050: premium cel.

This yields 47 semantic PASS / 3 WARN / 0 FAIL, with warnings at P003, P032, and P045; all selected hair/wardrobe checks pass. It has two adjacent route transitions, 31 fewer than the review-only hybrid, and zero within-sequence style transitions.

Preserve each narrative block as one style. Do not cherry-pick a differently styled panel inside a block. If a selected block later contains an explicit semantic FAIL, use the smallest same-style targeted repair. The current recommendation has no such failure and therefore requests no targeted repair.

Do not compile an executable, accepted, or promoted production manifest until the owner reviews or revises the assignments. A hash-bound review-only assembly may render the recommendation as a complete scroll while every acceptance, rights, commercial-clearance, and exact-base field remains false or null. The S01 choice is semantic/transition evidence, not a finish promotion: that five-panel route still contains lettering and strict-style failures.

## Consequences

The recommendation provides a coherent, measurable alternative to a 33-transition panel mosaic while preserving variable panel sizes and the ComicPanelPlan-only boundary. It does not prove palette, lighting, line-weight, facial micro-continuity, or environment continuity across the two remaining style boundaries. Owner acceptance, commercial-rights clearance, and exact-production-base selection remain null.
