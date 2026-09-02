# CH05 owner decision defaults r1

These are engineering recommendations, not recorded owner decisions. All ten decision fields remain null.

## Recommended pilot defaults

### 1. `route_role_aware_hybrid`

Recommended exact value: `CONFIRM_ROLE_AWARE_ROUTE`
Evidence: [style-engineering-results-r1.png](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-continuity-style-density-r1/style-engineering-results-r1.png)
Why: Unlocks prompt compilation only after candidate and reference choices are separately resolved.
Risk: Role-aware finishes can create visible style jumps if density and palette are not sequence-gated.

### 2. `c005_transition_density`

Recommended exact value: `REQUEST_EXACT_DENSITY_REDUCTION`
Evidence: [selected-phone-density-montage-r1.png](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-continuity-style-density-r1/selected-phone-density-montage-r1.png)
Why: Targets only c005; no broad transition reroll.
Risk: Current foliage density competes with the trail clue at phone size.

### 3. `c014_action_punctuation`

Recommended exact value: `KEEP_AS_ACTION_PUNCTUATION`
Evidence: [sequence-appearance-jumps-r1.png](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-continuity-style-density-r1/sequence-appearance-jumps-r1.png)
Why: Determines whether c014 remains in cadence or receives one finish-density repair.
Risk: Keeping the pulse preserves energy but accepts the largest measured adjacent appearance jump.

### 4. `lettering_semantics`

Recommended exact value: `KEEP_ACTION_AND_INSERT_BEATS_SILENT`
Evidence: [ch05-transparent-lettering-phone-comparison-r1.png](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/ch05-transparent-lettering-phone-comparison-r1.png)
Why: Any caption/speech change requires exact ComicPanelPlan semantics before layout.
Risk: Silence isolates causal evidence but may postpone necessary narrative clarification.

### 5. `lettering_visual_arm`

Recommended exact value: `USE_ROLE_DEPENDENT_88_OR_LIGHT_BAND`
Evidence: [ch05-outside-art-lettering-band-comparison-r1.png](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-outside-art-lettering-band-r1/ch05-outside-art-lettering-band-comparison-r1.png)
Why: Does not permit content overlap; final copy/font/tails/localization remain separate.
Risk: Role-dependent backing is more flexible but needs final copy, tail, localization, and accessibility review.

### 6. `p010_p013_finish_rhythm`

Recommended exact value: `USE_ROLE_AWARE_FOUR_BEAT_FINISH`
Evidence: [ch05-p010-p013-preflight-storyboard-r1.png](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-p010-p013-preflight-contract-r1/ch05-p010-p013-preflight-storyboard-r1.png)
Why: Controls only the next zero-prompt contract revision.
Risk: Four role-aware finishes maximize information but cannot prove uniform chapter continuity.

## Deferred recommendations

### 7. `p010_p013_copy`

Engineering default: `KEEP_SILENT_FOR_CAUSAL_TEST`
Recommendation: KEEP_SILENT_FOR_CAUSAL_TEST
Evidence: [ch05-p010-p013-preflight-storyboard-r1.png](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-p010-p013-preflight-contract-r1/ch05-p010-p013-preflight-storyboard-r1.png)
Risk: A silent causal test cannot validate final dialogue or caption layout.

### 8. `strongest_candidate_shortlist`

Engineering default: `REVIEW_INDIVIDUALLY`
Recommendation: Review all 14 individually; preserve engineering shortlist status without accepting as a group.
Evidence: [index.html](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/ch05-owner-review-index-r3/index.html)
Risk: Group-level taste approval cannot establish candidate-specific exact-base or rights status.

### 9. `noncanon_litrpg_direction`

Engineering default: `KEEP_ALL_NONCANON_PENDING_TASTE_REVIEW`
Recommendation: Advance Soren's oatmeal work-derived warden kit, Sigrid's plaid-preserving pathfinder kit, and the peat/root/slate Mireback together into a separate future-canon proposal, not a CH05 revision.
Evidence: [contact-sheet-future-litrpg-concepts.png](C:/AgentWorkspaces/anime-pipeline/experiments/review-packets/future-litrpg-visual-concepts-r1/review/contact-sheet-future-litrpg-concepts.png)
Risk: Kit continuity across the equipment sheets and Mireback scene is untested because new concept outputs were not re-uploaded.

### 10. `commercial_and_exact_base`

Engineering default: `REMAIN_OPEN`
Recommendation: Remain open pending candidate-specific visual review and an explicit rights/commercial decision.
Evidence: [ch05-pipeline-route-recommendation-r1.json](C:/AgentWorkspaces/anime-pipeline/production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json)
Risk: Provider rights, reproducibility, and exact-base suitability remain separate from visual quality.

## Exact six-root response template

If you want to unlock prompt compilation later, review and return these exact values through the established decision workflow:

- `route_role_aware_hybrid` → `CONFIRM_ROLE_AWARE_ROUTE`
- `c005_transition_density` → `REQUEST_EXACT_DENSITY_REDUCTION`
- `c014_action_punctuation` → `KEEP_AS_ACTION_PUNCTUATION`
- `lettering_semantics` → `KEEP_ACTION_AND_INSERT_BEATS_SILENT`
- `p010_p013_finish_rhythm` → `USE_ROLE_AWARE_FOUR_BEAT_FINISH`
- `p010_p013_copy` → `KEEP_SILENT_FOR_CAUSAL_TEST`

This does not cover candidate acceptance, commercial clearance, or exact-base selection.
