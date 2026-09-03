# ADR-0178: Fail closed on the chapter semantic graph before prompt promotion

- Status: Accepted
- Date: 2026-09-02

## Context

A structurally valid list of ComicPanelPlans can still be narratively incomplete or unsafe to promote: phases may be missing, display/sequence order can diverge, continuity state can disappear between panels, quiet lettering zones can be malformed, undeclared roles can appear, or armor/weapons/monsters can leak in through asset IDs without a canon decision.

## Decision

1. Validate the complete chapter as a semantic graph before any prompt, provider, output, or cost field exists.
2. Require exact six-phase declarations/coverage, stable unique panel/revision IDs, contiguous display order, 3-5-panel contiguous sequences, and exact sequence coverage.
3. Require all visible roles to be declared fictional adults; undeclared or child-coded roles fail.
4. Require at least one anchor scale, one small insert, and both high- and low-density beats.
5. Require valid normalized lettering-safe geometry or an explicit outside-art/gutter policy for every panel.
6. Require every adjacent continuity carry-out/carry-in edge and sequence entry/exit edge to match.
7. Require named progression asset prefixes to resolve to explicit canon decisions and asset allowlists.
8. Reject pre-promotion prompt/provider/model/service/output/cost/seed/reference fields anywhere in the graph.

## Consequences

- The synthetic positive graph passes and all 23 adversarial variants fail.
- The validator creates no North Garden story. Existing CH05 plans predate this richer graph contract and are evidence inputs, not claimed to conform retroactively.
- A future approved chapter can be checked before any external data boundary or rendering cost is involved.
