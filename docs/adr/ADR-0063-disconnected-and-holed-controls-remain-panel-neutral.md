# ADR-0063: disconnected and holed controls remain panel-neutral

- Status: accepted
- Date: 2026-09-01

## Context

P036 exercised one concave connected support and P044 one thin connected support. Holes and disconnected components were explicitly untested. Filling that mechanics gap could still be misused to infer a new panel profile or universal boundary width.

## Decision

Use fixed panel-neutral geometry: a ring with protected hole plus a separate 32px thin component. Compare 2/4/6/8/10/12/16/20px inward widths without changing geometry. Select only the widest local pass with exactly two nonzero/core components, at least 15% core in each feature, and exact hole/exterior preservation.

## Consequences

- Eight pixels is the widest pass; ring/thin core retention is 62.915%/25.936% with two core components.
- The protected hole and exterior have zero nonzero alpha and zero synthetic composite change.
- Twelve/twelve topology, tuning, width, hole, component, policy, review, and activity mutations fail.
- No panel profile, ComicPanelPlan policy, production mask, human review, renderer change, or external action follows.
