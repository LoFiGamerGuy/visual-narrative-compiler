# ADR-0091: Reserve full-width footprints for lettered anchors

- Status: accepted
- Date: 2026-09-01

## Context

Thirty local cases sweep one- and two-line non-canon copy at 88% backing across current-to-1200px footprints for c005, c013, and h001. c014 is excluded because its current safe zone already fails person clearance. The first 13px passes are c005 1200/1200, c013 1200/1200, and h001 1120/1200 for one/two lines. Consecutive builds preserve the same 31-artifact packet; 12/12 evidence mutations fail.

## Decision

Reserve near-full/full-width footprints for beats that actually carry balloons. Keep small clue, action, and object inserts silent or extremely low-text unless an explicit ComicPanelPlan revision provides a larger or outside-art lettering structure. Do not enlarge every panel: the cadence contract depends on alternating lettered anchors with quiet visual beats.

P040/c013 is a candidate for a large deduction anchor when final copy exists. P050/h001 can use 1120px for one short line or 1200px for two tested lines. P009/c005 should remain a quiet transition at its current width unless promoted to a full-width lettered beat. P044/c014 remains excluded pending plan-level placement repair.

## Consequences

- Phone type size becomes a layout input rather than a post-render shrink operation.
- The next smallest experiment tests an outside-art caption/dialogue band that might preserve narrow visual cadence without obscuring pixels.
- No measured width changes a ComicPanelPlan or current assembly.
- No copy, font, layout, art, or production base is accepted or commercially cleared.
