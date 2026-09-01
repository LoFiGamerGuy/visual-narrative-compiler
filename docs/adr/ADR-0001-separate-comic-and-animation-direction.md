# ADR-0001: separate comic-panel and animation-shot direction

Date: 2026-08-31  
Status: accepted

## Context

`research/historical/master-research-architecture-brief.md` proposes that animation extend a shared `ShotIR`. The current authoritative v2.1.1 corrections and handoff supersede that point. They preserve shared canon, assets, spatial information, and narrative intent, but identify comic panel direction and animation direction as different semantic records.

## Decision

Use:

`Canon / Story State -> Asset Registry -> SceneBeat / NarrativeIntent`

then branch to `ComicPanelPlan` or future `AnimationShotPlan / E-Conte`.

`RenderRecord` remains execution provenance and cannot be used as either directing record. Comic panels always declare one of `grounded`, `cheated`, or `2d_only`; intentional cheats are not automatic QA failures.

## Consequences

No animation-only fields will be added as null baggage to early comic plans. Both branches can reference the same characters, wardrobe, sets, poses, cameras, and accepted panel assets where useful, but neither is assumed to translate one-to-one into the other. This ADR records a material supersession rather than silently reconciling the historical proposal.
