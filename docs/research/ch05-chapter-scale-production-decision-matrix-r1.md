# CH05 chapter-scale production decision matrix r1

This is a review decision aid, not art acceptance, commercial clearance, canon replacement, or an exact production-base selection. The active structure remains ComicPanelPlan; AnimationShotPlan and E-Conte remain null.

## Measured facts

| Engineering rank* | Route | Semantics P/W/F | Overall P/W/F | Continuity-adjacent identity P/W/F | Lettering P/W/F | Style-density P/W/F | Cadence use |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | R6 | 47/1/2 | 49/1/0 | 50/0/0 | 50/0/0 | 0/0/0 (+50 not assessed) | 34 panels: s02-runnel-marker-trail, s03-listening-twine-ridge, s04-mill-reveal-bridge-warning, s05-creek-marker-drum, s06-ember-line-entry, s07-impossible-footprints-bell, s08-plank-tin-map |
| 2 | Premium cel | 40/5/5 | 40/5/5 | 50/0/0 | 50/0/0 | 0/0/0 (+50 not assessed) | 11 panels: s09-deduction-retreat-cut, s10-silence-return, s11-farmhouse-reversal |
| 3 | Clear-line watercolor | 45/2/3 | 45/2/3 | 50/0/0 | 50/0/0 | 0/0/0 (+50 not assessed) | 0 panels: none |
| 4 | Reduced-palette text control | 43/4/3 | 6/6/38 | 50/0/0 | 17/6/27 | 12/7/31 | 5 panels: s01-opening-departure |
| 5 | Alternate graphic | 36/7/7 | 36/7/7 | 50/0/0 | 50/0/0 | 0/0/0 (+50 not assessed) | 0 panels: none |
| 6 | Flat graphic-gouache | 41/6/3 | 16/7/27 | 50/0/0 | 19/6/25 | 0/0/50 | 0 panels: none |

*The rank is an engineering inference for the next chapter-scale review workflow, not a measured quality score. Style-density was not assessed for R6, alternate graphic, clear-line watercolor, or premium cel; unknown is not PASS. The continuity column is limited to identity/hair/wardrobe checks and does not establish finish continuity.

The selected review cadence is reduced-palette S01 (5 panels), R6 S02-S08 (34), and premium cel S09-S11 (11): 47 PASS / 3 WARN / 0 FAIL with two route transitions. Warnings remain at P003, P032, and P045. Human-reviewed and accepted counts remain zero.

P005-to-P006 remains a visual owner-review risk, but its matched three-arm attribution control supported a route-switch contribution on 0/2 histogram proxies. P039-to-P040 remains the lower observed boundary risk. Neither result grades art or supports a rerender.

## Engineering inference

1. **R6 — chapter backbone.** Largest selected share (S02-S08, 34 panels); highest semantic PASS count; 50/50 lettering and continuity-adjacent identity checks. Two supplemental semantic failures prevent wholesale promotion.
2. **Premium cel — late-block cadence specialist.** Selected for S09-S11 (11 panels) with zero selected semantic failures; wholesale route still has 5 semantic failures, so this is a block-specific inference.
3. **Clear-line watercolor — strongest unselected single-route fallback.** Best unselected wholesale semantic/overall profile after R6 (45/2/3) with 50/50 lettering and identity checks, but selected for no cadence block by the frozen objective.
4. **Reduced-palette text control — opening-block and lower-density specialist with finish constraints.** Selected only for S01 and is the only material lower-density separator; wholesale 38 overall failures, 27 lettering failures, and 31 style-density failures limit chapter-scale readiness.
5. **Alternate graphic — comparison route; not current production lead.** 50/50 lettering and identity checks, but 7 semantic and 7 overall failures and no selected cadence block.
6. **Flat graphic-gouache — diagnostic style arm; not current production lead.** Semantic 41/6/3 is outweighed for production review by 27 overall failures, 25 lettering failures, and 50 style-density failures; no selected cadence block.

Recommendation: retain the three-block cadence for owner review without promoting it to accepted production.

## Owner-review questions

- Does the assembled three-block cadence read as one coherent chapter at phone size, especially the two route boundaries?
- Is the visually abrupt P005-to-P006 cut acceptable as intentional beat contrast despite the route-switch proxy test being non-isolating?
- Are the three retained warnings acceptable or revision-worthy: P003 track overlap, P032 heel/toe direction, and P045 extra uphill building?
- Does provisional lettering preserve faces, hands, silhouettes, story objects, and phone readability across the full scroll?

## Future noncanon LitRPG exploration

These are ideation only and are not authorized for generation, canon, or production:

- Fictional-adult practical armor and upgraded clothing silhouettes that preserve role and hair readability.
- Weapons/tools designed around causal grip, leverage, carry continuity, and readable action rather than decorative posing.
- Monster/ecology encounter beats and restrained LitRPG system feedback that create tactical story consequences instead of generic spectacle.

## Exactly one next experiment

**ch05-cadence-objective-sensitivity-audit-r1:** Use only the existing six-route per-panel evaluation table. Re-run the 11-sequence cadence optimizer under leave-one-secondary-objective-out variants while preserving hard zero semantic/identity-failure constraints; report whether the current three-block assignment remains invariant or expose the Pareto alternatives.

Why: This tests whether the recommended cadence is robust evidence or an artifact of lexicographic tie-breaking before more art or repair effort is spent. It requires no provider, upload, new pixels, or paid spend.

## Bound inputs

- `docs/research/ch05-complete-chapter-review-handoff-r7.md` — SHA-256 `739cf2766edf816f24b0296253245d13ad7298cddf1b61286c43af999e065686`
- `docs/research/evidence/ch05-six-route-comparison-r1.json` — SHA-256 `c40d3a945704639855135cda4d011529f13c5c71d857b7807914823d7e248229`
- `docs/research/evidence/ch05-sequence-cadence-review-triage-r1.json` — SHA-256 `d99b34c94c6037a5e45c175f5847f316eb141ae35dd78774410ebd1033657e1c`
- `docs/adr/ADR-0188-use-measured-sequence-level-cadence.md` — SHA-256 `6b39c94d080b334a6eb03ea61f3a2eaa36967b06f060f2c7050f23228472ca82`
- `docs/adr/ADR-0189-treat-paired-reference-ablations-as-directional-evidence.md` — SHA-256 `28b6c5d9020ac6aaa1d641813592ca6728d0095933ee76138d250f446e6904c2`
- `docs/adr/ADR-0190-treat-p005-p006-as-a-finish-continuity-risk.md` — SHA-256 `853cea56fe0459130477c3d708326284913a821924c8e06207d97c6456d8ae5e`
- `docs/adr/ADR-0191-do-not-rerender-p005-p006-from-nonisolating-proxies.md` — SHA-256 `f1c9cdd03513a2d519bef5b1a4ebd3d7d3c07caeb2dc3ad35ee59ab447e11748`

The machine-readable record is `docs/research/evidence/ch05-chapter-scale-production-decision-matrix-r1.json`.
