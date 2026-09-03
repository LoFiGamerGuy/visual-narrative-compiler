# ADR-0175: Freeze CH05 r6 release and do not invent missing CH01-CH04 chapter plans

- Status: Accepted
- Date: 2026-09-02

## Context

CH05 r6 now binds a complete 50-panel ComicPanelPlan reading draft, eight owner-review artifacts, and 49 PASS / 1 WARN / 0 FAIL non-gating triage. The source inventory also contains CH01-CH04 ComicPanelPlan collections, but each represents only one 3-4-panel scene fragment. Calling those fragments completed chapters, or filling their missing story beats without a chapter-scale canon source, would blur engineering progress with unreviewed narrative invention.

## Decision

1. Freeze CH05 r6 as the current complete-chapter owner-review baseline.
2. Bind the release to exact source and artifact hashes; keep generated pixels ignored and unaccepted.
3. Preserve P032 as the sole explicit warning rather than spending more low-information stochastic attempts.
4. Treat CH01-CH04 as continuity and pipeline-regression material only.
5. Do not render or label another complete chapter until a chapter-scale ComicPanelPlan collection exists. Continue local reusable-pipeline hardening in the meantime.
6. Keep ComicPanelPlan as the only production-planning structure; AnimationShotPlan and E-Conte remain null.

## Consequences

- The user receives a coherent complete CH05 review unit rather than more disconnected probes.
- Existing earlier-chapter fragments remain useful for cross-chapter identity, wardrobe, lettering, and assembly regression tests.
- A future chapter-scale plan may be authored or approved separately, with its canon decisions visible rather than silently embedded in prompts.
- This decision creates no acceptance, commercial clearance, exact-production-base status, provider permission, upload class, or spend authority.
