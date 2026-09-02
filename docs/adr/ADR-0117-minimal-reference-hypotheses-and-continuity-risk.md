# ADR-0117: Minimal reference hypotheses and continuity risk

Date: 2026-09-01

Status: Accepted as a metadata-only plan

## Context

Hair color/style, wardrobe, role order, and extra-person drift are production risks. More references are not automatically safer: Soren-only panels must use a dual-character identity anchor, and P036 has useful composition but swapped hair colors. A chapter-scale plan must minimize reference use while preserving explicit guards.

## Decision

- Keep all 18 no-person plans text-only.
- Use P040 for Sigrid-only identity; use P050 for Soren-only identity with a high-risk single-cast/extra-person guard.
- Use P050 as the minimum dual-cast anchor; add P040 only for the role classes that need closer Sigrid/dual continuity.
- Use P036 exactly once, for P036 composition metadata only, with `identity_authority: NONE` and a critical swapped-hair guard.
- Require manual hair, wardrobe, cast, role, anatomy, hands/object, lettering, and phone checks; prohibit automated identity inference.

## Evidence

- 50 plans, 42 metadata reference hypotheses, and 18 text-only rows.
- P050 appears in 25 hypotheses; P040 in 16; P036 composition-only in one.
- Continuity risk classes: 18 low, nine medium, 22 high, one critical-guarded.
- The 1600×1900 risk map is visually checked.
- Attempt 1's 43-reference hand estimate is preserved; deterministic row rules produced 42 and were not inflated to satisfy the estimate.
- 20/20 mutations are rejected.

## Consequences

- This record does not perform or authorize an upload.
- High risk means stricter preflight/manual review, not that a panel is unsuitable.
- Reference count is minimized by cast/role; it is not a quality score.
- Prompts, identity inferences, acceptance, execution, calls, and cost remain zero.
