# ADR-0064: generic topology coverage does not increase panel-profile count

- Status: accepted
- Date: 2026-09-01

## Context

The disconnected/hole control adds a locally selected 8px width. Folding it into selector r1 or counting it as a third panel profile would rewrite prior evidence and imply ComicPanelPlan applicability that was never tested.

## Decision

Issue append-only selector r2, pinning r1 exactly. Preserve P036=16px and P044=5px profiles unchanged. Record the disconnected/hole 8px result under `panel_neutral_mechanics_controls` with profile, policy, and visual-acceptance eligibility all false.

## Consequences

- Topology-control passes increase from two to three while panel profiles remain two.
- Universal width remains null; exact-panel visual passes, timed seam reviews, and production-ready profiles remain zero.
- Thirteen/thirteen supersession, width leak, profile/policy/visual promotion, summary, and generalization mutations fail.
- Existing r1 consumers and immutable evidence remain valid; r2 grants no new production input or action.
