# ADR-0217: Use corner safe-zone semantics for sparse local lettering

## Status

Accepted for the CH06–CH13 local-lettering review route. Copy and derivative pixels remain review-only and unaccepted.

## Context

The 320 ComicPanelPlans store `rect_norm` values such as `[0.66, 0.04, 0.96, 0.20]`. These are left/top/right/bottom corners. Treating the final pair as width/height pushes right-anchored boxes outside the panel and clips copy. Historical overlay builders contain that interpretation and cannot be silently rewritten without invalidating their recorded hashes.

## Decision

1. Interpret every lettering safe zone as normalized corner coordinates.
2. Preserve historical artifacts and manifests unchanged as diagnostic evidence.
3. Author exactly ten sparse beats per chapter for CH06–CH13 and render them locally with translucent backings.
4. Create compact ten-beat phone packets in addition to complete 40-panel scrolls.
5. Preserve source art triage and acceptance boundaries; lettering cannot promote a source candidate.

## Evidence

Eighty unique copy bindings cover eight chapters. The corrected deterministic builder produces 25 artifacts from 320 source candidates and passes 10/10 mutation tests. All copy fits the canonical corner boxes at source resolution. The copy distribution is 49 dialogue, 15 system, 10 SFX, and 6 captions.

## Consequences

The full Bell Road arc is now readable as sparse local-lettering story evidence without re-generating pixels or burning prose into art. Right-anchored copy no longer clips. Historical safe-zone overlays must be read as planning diagnostics rather than authoritative placement previews until separately superseded.
