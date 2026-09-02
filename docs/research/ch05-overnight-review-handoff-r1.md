# CH05 overnight review handoff r1

Status: provisional engineering review complete; owner candidate review pending. No output is accepted, commercially cleared, or an exact production base.

## What to compare

- Story direction and role order: c001 versus c019.
- Reference benefit at the bridge: c006 versus text-only c007.
- Causal cooperation: c011 versus c012.
- Sigrid deduction continuity: c013 versus text-only c020.
- Urgent-return density: c017 versus c018.
- Chapter cadence: c017 → c013 → c014 → c015 → c016, with c018 as the lower-density wide alternative.

## Provisional recommendation

Use a premium cel-painted finish with clear-line contour hierarchy for character and causal-action panels, and retain clear-line watercolor composition for wide/transition panels until the missing cel-painted P050 wide comparison passes. Use genuinely simplified limited ink for inserts. Preserve P050/P040 as identity references and P036 as composition-only.

## Review state

- 20 candidates, 14 ComicPanelPlans, three sequences, four style families.
- 12 all-six-dimension engineering passes, three warn-only, five with failures.
- 919.389 seconds observed generation time; monetary cost and provider metadata unavailable.
- Human reviewer/session/minutes/acceptance remain null/pending.

The ignored local review packet is `experiments/review-packets/ch05-overnight-production-r1/review/review-packet.json`; tracked exact evidence is `docs/research/evidence/ch05-overnight-production-r1.json`.

## Cadence-hardening addendum

Six additional candidates close the cel-painted wide-action gap and repair c003/c007/c009. Compare c011 → h005 → h006 to see why plan-literal single-plank wording outperforms lever terminology for P036. Hardening evidence is `docs/research/evidence/ch05-cadence-hardening-r1.json`; the ignored local packet is `experiments/review-packets/ch05-cadence-hardening-r1/review/review-packet.json`.

## Separate non-canon concept review

l001/l002/l003 explore future equipment and a Mireback encounter without revising CH05. Exact kit replication across l003 is not claimed because l001/l002 were not re-uploaded. Tracked evidence is `docs/research/evidence/future-litrpg-visual-concepts-r1.json`; the ignored packet is `experiments/review-packets/future-litrpg-visual-concepts-r1/review/review-packet.json`.

## Variable-cadence assembly addendum

The strongest 14 provisional candidates now form three connected sequences in a deterministic phone-first scroll. Review the clean 1200px scroll, exact safe-zone overlay, 390px phone scroll, seven viewport slices, and three selected-sequence sheets under `experiments/review-packets/ch05-variable-cadence-assembly-r1/`. Tracked evidence is `docs/research/evidence/ch05-variable-cadence-assembly-r1.json`.

ADR-0089 recommends variable width/alignment/gutter cadence rather than a uniform panel ratio. Hair, wardrobe, role order, and causal flow pass provisional engineering review. c005 and c014 remain explicit lettering-rehearsal warnings, and mixed finish density remains an owner decision. No panel or sequence is accepted.

## Transparent-lettering addendum

Review `experiments/review-packets/ch05-transparent-lettering-rehearsal-r1/ch05-transparent-lettering-phone-comparison-r1.png`. The 88% backing is the strongest next arm, but none of the four tested panels reaches the declared 13px two-line phone target. c014's tested balloon also overlaps Soren's person/upper-arm area and fails outright. ADR-0090 therefore keeps P044 silent unless its ComicPanelPlan lettering strategy is revised. Tracked evidence is `docs/research/evidence/ch05-transparent-lettering-rehearsal-r1.json`; no treatment is accepted.

The follow-up width/copy sheet is `experiments/review-packets/ch05-lettering-width-copy-sensitivity-r1/ch05-lettering-width-copy-sensitivity-r1.png`. At 88% backing, c005/c013 first reach 13px only at 1200px; h001 reaches it at 1120px for one line or 1200px for two. ADR-0091 therefore recommends full-width lettered anchors alternating with quiet smaller panels. Tracked evidence is `docs/research/evidence/ch05-lettering-width-copy-sensitivity-r1.json`; these are layout measurements, not plan revisions or accepted lettering.

The outside-art alternative is `experiments/review-packets/ch05-outside-art-lettering-band-r1/ch05-outside-art-lettering-band-comparison-r1.png`. Both arms keep the narrow art footprints, render 13.975px phone copy, and change zero source pixels. The light band groups copy with the next panel more clearly; dark direct text is quieter. ADR-0092 limits both to caption/direct-text geometry, not character speech. Tracked evidence is `docs/research/evidence/ch05-outside-art-lettering-band-r1.json`; P044 still needs a ComicPanelPlan revision before any text.

## Single review entry point

Open `experiments/review-packets/ch05-owner-review-index-r1/index.html` for all 29 candidates, the selected 14, sequence/cadence packets, lettering alternatives, diagnostics, and the three separate non-canon LitRPG concepts. The exact nonexecutable row manifest is `production/comic/run-manifests/ch05-instrumented-production-manifest-r1.json`; tracked evidence is `docs/research/evidence/ch05-instrumented-production-handoff-r1.json` and `docs/research/evidence/ch05-owner-review-index-r1.json`. No selection in the index is accepted.

Review `experiments/review-packets/ch05-continuity-style-density-r1/selected-phone-density-montage-r1.png` and `experiments/review-packets/ch05-continuity-style-density-r1/sequence-appearance-jumps-r1.png`. The largest review question is c013→c014→c015: calm deduction, dense limited-ink cut, calm cel-painted protection. Decide whether that pulse is exciting intentional rhythm or an unwanted finish discontinuity. c005 is the other exact density concern. Tracked evidence is `docs/research/evidence/ch05-continuity-style-density-r1.json`; metrics do not recognize identity or accept art.

The full 50-plan coverage map is `experiments/review-packets/ch05-remaining-panel-priority-r1/ch05-coverage-priority-map-r1.png`. Green is the selected 14; blue/gold/gray are exact Tier A/B/C 12-panel tranches. ADR-0096 recommends Tier A only after current owner review, concentrating on coherent trail/twine and mill/red-cloth chains rather than more isolated hero art. Tracked evidence is `docs/research/evidence/ch05-remaining-panel-priority-r1.json`; no new generation is authorized or implied by the map.

Tier A's provisional style/size hypotheses are in `production/comic/coverage/ch05-tier-a-production-hypotheses-r1.json`; observed effort scenarios are `docs/research/evidence/ch05-tier-a-effort-scenarios-r1.json`. The empty 39-subject review intake is `production/comic/review/ch05-owner-decision-contract-r1.json`. Monetary cost and human review time are deliberately null; no Tier A prompt or execution authority exists.

For a single decision-oriented surface, open `experiments/review-packets/ch05-owner-decision-worksheet-r1/index.html`. It binds all 39 pending subjects and exports only a local `LOCAL_UNINGESTED_DRAFT`; it cannot record acceptance or alter the contract. Tracked build evidence is `docs/research/evidence/ch05-owner-decision-worksheet-r1.json` under ADR-0099.

Exported worksheet JSON can be checked with `python src/north_garden/validate_ch05_owner_decision_draft.py <draft.json>`. A passing result means only that the local draft matches the empty contract; it does not create a review event or accept anything. Synthetic boundary evidence is `docs/research/evidence/ch05-owner-decision-draft-validator-r1.json` under ADR-0100.

Hair/wardrobe drift controls are compiled in `production/comic/continuity/ch05-character-assertion-manifest-r1.json`. All 26 generated CH05 prompts contain the expected explicit constraints, but this does not prove their pixels; compare rendered hair, wardrobe, role staging, and anatomy manually. Tracked lint evidence is `docs/research/evidence/ch05-character-assertion-and-prompt-lint-r1.json` under ADR-0101.

Open `experiments/review-packets/ch05-manual-continuity-atlas-r1/ch05-continuity-atlas-all-26-r1.png` for every alternate grouped by plan and `experiments/review-packets/ch05-manual-continuity-atlas-r1/ch05-continuity-atlas-selected-14-r1.png` for narrative order. These are full-panel manual aids with no face crops or identity inference. Tracked evidence is `docs/research/evidence/ch05-manual-continuity-atlas-r1.json` under ADR-0102.

Review `experiments/review-packets/ch05-panel-scale-cadence-policy-r1/ch05-panel-scale-cadence-map-r1.png` for the proposed chapter rhythm. It recommends ranges by narrative function rather than one aspect ratio; copy can force a 1,200px test or a semantic plan revision. Tracked policy is `production/comic/layout/ch05-panel-scale-cadence-policy-r1.json` with evidence under ADR-0103.

Review `experiments/review-packets/ch05-failure-class-repair-matrix-r1/ch05-targeted-repair-paths-r1.png` for the exact repair evidence. ADR-0104 recommends literal single-object/role wording and selects P010–P013 as the smallest next continuity microsequence after owner review. The matrix is `production/comic/review/ch05-failure-class-repair-matrix-r1.json`; it contains zero prompts or execution authority.

Review `experiments/review-packets/ch05-p010-p013-preflight-contract-r1/ch05-p010-p013-preflight-storyboard-r1.png` for the four-row continuation hypothesis. The tracked contract is `production/comic/repair-readiness/ch05-p010-p013-preflight-contract-r1.json`; its prompts/outputs are null and its two repair slots remain unallocated under ADR-0105.

The current single entry point is `experiments/review-packets/ch05-owner-review-index-r2/index.html`. It extends r1 without rewriting it and links the decision worksheet plus every post-r1 continuity, cadence, repair, and preflight artifact. Tracked evidence is `docs/research/evidence/ch05-owner-review-index-r2.json` under ADR-0106.

Current release integrity is `docs/research/evidence/ch05-overnight-integrated-release-gate-r3.json`. The failed first attempt is retained separately; manifest r2 rebinds the current registry while preserving the original 14-row root. ADR-0107 records why this is append-only rather than an r1 rewrite.

Review `experiments/review-packets/ch05-chapter-scale-production-envelope-r1/ch05-chapter-scale-production-envelope-r1.png` for measured remaining-chapter scenarios and cadence-role demand. The tracked envelope is `production/comic/run-manifests/ch05-chapter-scale-production-envelope-r1.json`; monetary cost and human minutes are deliberately null under ADR-0108.

Review `experiments/review-packets/ch05-renderrecord-completeness-audit-r1/ch05-renderrecord-field-matrix-r1.png` for the all-candidate evidence matrix. The tracked index is `production/comic/run-manifests/ch05-built-in-renderrecord-index-r1.json`: 29 exact records, 39 reference uses, and 1,385.036 observed seconds. Model, endpoint, request ID, provider usage, monetary cost, and seed are explicit null in all 29 records. ADR-0109 also records the append-only 0.788-second correction to earlier concept/total narrative timing. All candidates remain pending and unaccepted.

Current release integrity is now `docs/research/evidence/ch05-overnight-integrated-release-gate-r4.json`: immutable r3 plus three extensions gives 33 effective checks, 4/4 commands pass in 6.934 seconds, and 23/23 mutations fail under ADR-0110.

The current single review entry point is now `experiments/review-packets/ch05-owner-review-index-r3/index.html`. For exhaustive direct links, use `docs/research/ch05-review-links-r1.md`: it resolves 99 unique artifacts including every current CH05 contact sheet, sequence deliverable, lettering overlay/comparison, and the 14-candidate provisional engineering shortlist. ADR-0111 keeps every linked pixel ignored, unpublished, unaccepted, and commercially uncleared.

The current engineering route is `production/comic/recommendations/ch05-pipeline-route-recommendation-r1.json`, with ten remaining choices in `production/comic/review/ch05-route-review-decision-matrix-r1.json` and ComicStyleDirection r10. ADR-0112 recommends role-aware cel-painted character/action anchors, clear-line causality/transitions, selected clean-graphic blocking controls, and exact-density-gated simple inserts; it does not accept a candidate, commercial route, or exact production base.

The next microsequence's fail-closed production shape is `production/comic/run-manifests/ch05-p010-p013-production-manifest-dry-run-r1.json`. It contains four exact ComicPanelPlan rows, two bounded repair slots, five planned review artifacts, and no prompt or executable state under ADR-0113.

Its pre-render review semantics are `production/comic/review/ch05-p010-p013-review-packet-contract-dry-run-r1.json`: 11 checks per slot, five unbuilt artifacts, 11 failure classes, and five promotion rules under ADR-0114. This record creates no review event or acceptance.

Integrated evidence now passes release r5 at `docs/research/evidence/ch05-overnight-integrated-release-gate-r5.json`: 38 effective checks, 6/6 commands, and 26/26 rejected mutations under ADR-0115.

Review the full 50-plan readiness map at `experiments/review-packets/ch05-chapter-production-readiness-r1/ch05-chapter-readiness-map-r1.png`. The tracked matrix is `production/comic/run-manifests/ch05-chapter-production-readiness-matrix-r1.json`; ADR-0116 keeps every prompt and promotion gate closed.

Review the hair/wardrobe/reference risk map at `experiments/review-packets/ch05-reference-use-continuity-risk-r1/ch05-reference-risk-map-r1.png`. The tracked plan is `production/comic/continuity/ch05-reference-use-and-continuity-risk-plan-r1.json`; ADR-0117 makes all 18 no-person rows text-only and critically guards the sole P036 composition hypothesis.

Future owner-review time can be measured with `production/comic/review/ch05-human-review-time-instrumentation-contract-r1.json` and `python src/north_garden/validate_ch05_human_review_time_event_log.py <event-log.json>`. ADR-0118 forbids backfilling prior review; current minutes remain null.

Use `docs/research/ch05-owner-handoff-checklist-r1.md` for the 24-task dependency-ordered review path. ADR-0119 separates parallel candidate/foundational review, dependent P010/lettering choices, optional non-canon taste review, and final commercial/exact-base authority.

Integrated evidence now passes release r6 at `docs/research/evidence/ch05-overnight-integrated-release-gate-r6.json`: 42 effective checks, 5/5 commands, and 26/26 rejected mutations under ADR-0120.

Review the 12 coherent chapter batches at `experiments/review-packets/ch05-chapter-sequence-production-batches-r1/ch05-sequence-batch-map-r1.png`. The tracked manifest is `production/comic/run-manifests/ch05-chapter-sequence-production-batches-r1.json`; ADR-0121 keeps production wave distinct from story order and every prompt null.
