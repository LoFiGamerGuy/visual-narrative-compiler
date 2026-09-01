# ADR-0071: hardening handoff r2 advances pointers, not renderer claims

- Status: accepted
- Date: 2026-09-01

## Context

Selected-route handoff r1 correctly preserves the measured bakeoff and blocked production state, but it references earlier budget, selector, rebuild, source, and ledger revisions. Rewriting r1 or copying new readiness counts into its old provenance would make the handoff ambiguous.

## Decision

Issue handoff r2 with an exact r1 supersession binding. Preserve the selection, G07 measured state, 50-panel readiness, and P036 fail-closed state byte-for-byte. Advance only cross-evidence pointers and measured local coverage/release metadata.

## Consequences

- OpenAI remains an engineering hardening route based on the original measured dimensions, not visual appeal or art acceptance.
- G07 remains 0/20 decisions/null minutes/zero accepted; CH05 remains zero approved inputs, outcomes, accepted panels, and production cost.
- Latest evidence records three topology passes/two panel profiles, 28 rebuilt artifacts/nine groups, a 60/60 release gate, 387-path safe-source release, five root authority items, and 37 zero-cost milestones.
- Eighteen/eighteen selection/review/profile/authority/release/activity mutations fail; `next_external_action` remains null.
- No provider request, upload, budget grant, commercial clearance, or production promotion follows.
