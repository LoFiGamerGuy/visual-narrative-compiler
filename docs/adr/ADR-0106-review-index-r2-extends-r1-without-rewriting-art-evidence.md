# ADR-0106: Review index r2 extends r1 without rewriting art evidence

- Status: accepted
- Date: 2026-09-01

## Context

Owner review index r1 remains the exact entry point for the 29 candidates and original art/sequence/lettering packets. Later continuity, cadence, repair, and preflight artifacts should be reachable from one surface without altering r1 or the empty 39-subject decision contract.

## Decision

Create local review index r2 as an append-only hub that hash-binds r1 and the decision worksheet. Link seven exact resources: two HTML entry points and five post-r1 visual artifacts. Include no remote assets, forms, network code, or decision-writing behavior.

## Consequences

- R2 presents 29 candidates, 14 provisional selections, 39 pending decision subjects, and all 50 ComicPanelPlans from one page.
- Seven links and six local index artifacts build byte-identically; 13/13 mutations fail.
- R1, the worksheet, and the decision contract remain unchanged.
- Decisions, accepted candidates, review minutes, calls, uploads, and cost remain 0/0/null/0/0/$0.
