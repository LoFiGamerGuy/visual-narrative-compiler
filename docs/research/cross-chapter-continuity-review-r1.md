# Cross-chapter continuity review r1

This packet compares all 13 current CH01-CH04 scene-fragment panels with ten story/continuity anchors from the complete CH05 r6 draft. It is a mixed-era diagnostic, not a renderer benchmark or an acceptance decision.

## Review artifacts

1. [Chapter-row contact sheet](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/cross-chapter-comic-regression-r1/cross-chapter-comic-regression-contact-sheet.png) — 1800 × 1300, SHA-256 `285c412fbf166347a0884fbf341098b1df42debd19fc172043b2947d0b0b16b3`.
2. [Phone-width progression](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/cross-chapter-comic-regression-r1/cross-chapter-comic-regression-phone-scroll.png) — 390 × 7871, SHA-256 `417136fb35cd435f1dd864fa282f40aab12b0efd6a88eccbc3889a8b7bc11b7d`.

## Non-gating visual observations

- Hair/color identity drift is substantial across renderer eras. CH02-CH04 generally use very dark-haired Soren and auburn/red-haired Sigrid; CH05 uses light-brown/dark-blond Soren and dark-haired Sigrid.
- CH02 also has the largest wardrobe/weapon discontinuity relative to CH05. Preserve it as historical evidence, but do not use it as a new-generation identity reference.
- CH03-CH04 have strong low-light atmosphere and causal blocking, but faces and silhouettes lose phone-width separation more often than CH05.
- CH05's restrained clear-line watercolor/cel hybrid gives the clearest phone-scale action and object causality. P036's tall leverage beat and P039/P043 object beats demonstrate the strongest variable-cadence improvement.
- CH01's warm graphic interiors are useful as a future lower-density interior-style reference, but the distant figures are weak identity anchors.

## Recommendation

Use the CH05 r14 hair/wardrobe contract as the provisional target for future generation, while preserving earlier editions unchanged. Replacing an accepted historical panel should create a new immutable PanelRevision and edition selection after owner canon review. Introduce armor, weapons, upgraded clothing, and monsters only through an explicit future ComicPanelPlan/canon proposal.

Evidence: [tracked regression record](C:/AgentWorkspaces/anime-pipeline/docs/research/evidence/cross-chapter-comic-regression-r1.json), [chapter inventory](C:/AgentWorkspaces/anime-pipeline/docs/research/evidence/comic-panel-plan-chapter-inventory-r1.json), and [ADR-0176](C:/AgentWorkspaces/anime-pipeline/docs/adr/ADR-0176-use-ch05-hair-and-wardrobe-contract-for-future-generation-without-rewriting-historical-selections.md).
