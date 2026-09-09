# Five-pilot reading review — v2

AI editorial and visual inspection, not owner acceptance. No new art invocations. All 80 selected source files and their SHA-256 bindings are unchanged. Original edition and original copy are preserved.

## Observed baseline

Read all five complete 390px continuous capture sequences from the completed worktree, and inspected all 80 selected native panels in four-panel strips. The baseline's exact copy is readable but repeated speaker labels, in-comic “off panel” terminology, controls, feedback forms and uniform framing repeatedly interrupt the story. NG02, NG13, BP04, ST02 and RC15 show speaker geography opposite the fixed balloon order. The visual failures listed below are observations of the artwork, not inferred from descriptions.

## Resulting edition

The entry point now opens a comic with series title, premise, first-scene link and five clear story choices. Native image aspect ratios and authored larger gaps are retained. Review controls and provenance are on a separate route. Speech is still editable HTML with SVG tails; no raster letters were painted into artwork. Main dialogue is 16 CSS px at 390px width. Added lettering space is used for the specific crowded or reversed compositions. It reveals all faces, handoffs and contacts in those panels and retains dialogue order.

Black Petal's borrowed phrase uses a consistent pale rose, italic, double-border balloon. The reader never labels it as the bloom before the reveal. Visible speaker names are mostly removed. Small offscreen names retain useful attribution with frame-edge tails. NG07 keeps small Pell/Aren cues because both people occupy almost the same horizontal coordinate at different heights; ST15 keeps Tavi's small cue because a short upward tail otherwise points at the ram beneath her. These are deliberate residual attribution aids, not production labels.

Three line changes are recorded in `production/pilots-reading-v2/copy-revisions.json`: BP12's two escape-time jokes become a direct escape instruction and Neris's relief; FL12's quip becomes “Keep pulling.” Nightglass's disappointed ambition, Black Petal's failed voice test and nursery clue, Soft Thunder's negotiation and independent ram, Red Current's earned key and debt, and Floodline's missing-person rescue and Authority clue retain their original story roles.

## Actual iteration

The first v2 capture exposed a regression: generic balloon placement put NG09's speech over the ray and made RC09's balloon crowd Ren. Restored selected-source placement decisions rather than trusting a global formula. Shortened tail tips before faces. The first NG07 and ST15 marginal tails were insufficient to distinguish vertically aligned people or rider/ram; retained minimal explicit name cues for those specific cases. Offscreen tails now point horizontally out of the frame rather than toward incidental nearby fauna. Earlier draft and interim captures are retained separately.

## Remaining artwork failures

- NG09 and NG10: the cyan force line visibly joins or crosses the blade/beak contact rather than remaining one pommel-to-anchor line. The rescue outcome is broadly legible; the stated mechanism is not reliably shown. NG07 also has ambiguous line origin behind Aren. Do not reuse these as evidence that the tether topology is solved.
- ST11→ST12: the circular gauntlet charges; the crescent gauntlet emits the puff. Padding and the ram's relaxed response are legible, but equipment causality is contradictory. ST10 also regularizes the glove symbols. This edition does not change the power rule to excuse the art.
- RC: charged anatomical side and the key's shape drift. The receiving gauntlet in RC05 does not preserve the stated right-side inventory. RC13/14 retain visible wrist cost but the key varies. RC15 keeps the dim source; the brighter finishing attempt is not selected.
- FL05: concentric ripples remain present with the visible memory, contradicting the still-water condition. FL10–12 show rescue effort but do not clearly establish the two physical pole-head jaw contacts. Lettering leaves the actual evidence unobstructed.
- BP: the flower's root severing is broadly legible. The selected native art still has some cast/gear variability and attractive but repeated figure scale. The voice test and Neris's escape remain the most complete emotional causal sequence among the secondary pilots.

## Reading limitations

Added margins protect the source artwork but sometimes make a dialogue exchange taller and slower than a composition drawn for lettering from the start. Marginal tails point toward a speaker's region rather than touching the face. NG07 and ST15 therefore keep specific minimal names; absence of production labels is not claimed as universal absence of names. No ratings or owner preferences were invented. This is a practical improved reading edition, not a claim that every art or continuity defect has been repaired.

Final capture receipt and continuous images: `phone-v2/`. Browser checks are reported separately in `phone-v2/browser-check.json`; visual completion is recorded after reading those actual outputs below.

## Completed final checks

Read every frame of all five final continuous sequences in `phone-v2/`: NG 13 captures, BP 13, ST 11, RC 11 and FL 13. All 80 selected lettered panels appear in those complete sequences and are also saved separately at 390px. The lettering can be read at its actual displayed size; added margins leave the close faces and object handoffs fully visible. The final browser receipt records 16 panels per chapter, no failed image loads, no JavaScript errors, no horizontal overflow and all dialogue balloons inside the viewport at 16 CSS px. Independently recomputed all 80 native SHA-256 hashes: all matched.

The complete read exposed a header-level reveal problem: inherited synopses summarized each ending before the first panel. Replaced only the reader's introductory blurbs with short premises that establish the situation without disclosing the outcome. The originals remain in chapter metadata; new blurbs are explicit `reading_premise` fields. Final header captures at `entry-v2/` were each visually inspected. `phone-v2/` remains the inspected complete comic/lettering capture; only its header copy predates this final blurb change. No panel, balloon, tail, art, gap or story order changed afterward.

Observed story assessment: NG retains a persuasive choice, real frustration and an earned lower-city invitation; BP's voice repetition now belongs consistently to the uncanny speaker and the rescued caretaker gets room for relief; ST's warmth and negotiation survive the clarified order; RC retains a visible earned key before its cost; FL's extraction reads with immediate urgency. None of those reading improvements establishes correct tether, charge-side or jaw-brace mechanics where the raster itself remains contradictory.

Independent editorial spot-check subsequently identified residual misleading tails in NG07 (vertically aligned Aren and Pell) and ST15 (Tavi above the ram). Removed those three tails while retaining compact speaker names. This specific correction avoids a contradictory visual attribution cue without inventing a different pose or hiding speech. Final corrected panel captures are in `attribution-final/`; all other story lettering remains as the complete `phone-v2/` reading. The reader data expresses this as `name_cue: true, no_tail: true`.

Later independent longform review found the reused NG11 diagonal staging also made its short marginal tails visually misleading. V2 NG11 now uses compact Pell/Aren speaker names and no tails, matching the corrected NG07 treatment. Actual corrected390px capture `attribution-final/NG11-verified.png` was inspected. Exact story copy and native art remain unchanged. The corresponding longform N1-18 uses the same correction.
