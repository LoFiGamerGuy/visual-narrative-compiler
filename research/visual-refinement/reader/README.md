# Offline refinement readers

Open `docs/research/visual-refinement/index.html` for the controlled and exploratory boards. The direct **Read the six-panel tests** link opens `sequence.html`. Both pages use local scripts and images, with no server, external font or network script.

## Owner workflow

The nine historical stars label original style references only. All responses to new images begin blank, and the new shortlist uses a separate plus/check control. Character appeal, drawing treatment, readability and visual comfort each support an independent positive, negative or unsure response. Clicking an active response clears it. Notes remain separate from the frozen briefs and artwork.

Switch **A / Iven** and **B / Mara** to see the same retained character across the nine styles. A chosen comparison lineup follows the same style IDs when switching character, where the counterpart art is available. Select two or three boards and use the floating comparison tray. Desktop comparisons share a row; phone comparisons stack full images. Exploratory X1/X2 are a separate view and cannot join a controlled comparison lineup.

Tap an image for a complete fit view or native pixels. Native links also appear in **Brief & references**. Escape closes the top image dialog first, returning to an open comparison. Missing candidates have explicit placeholders and disabled responses. A file that fails to load produces a visible missing-art state and disables new responses to that image; previously saved choices remain intact.

**Compare with original reference** shows the owner's earlier starred board beside the new output. The original has a different cast/world and is explicitly identified as a drawing reference, not a controlled cast pair. The UI states that framing, body and creature can drift despite the same brief. When final source-bound notes are supplied, **AI visual observations** appears as a separate collapsed section; those observations never set owner responses.

For comparison boards or sequence panels, if a selected image is a repair, **View repair comparison** presents its retained primary and selected retry, with native images, attempt IDs, image hashes and a source-record link/hash. The declared hard failure appears above the pair. The four comparison treatment repairs and later sequence corrections use revised reference conditioning and the view explicitly states that this is not an identical-input experiment. This view has no voting controls and does not claim that the repair succeeded. The R candidate or its existing `calls/<attempt_id>.json` record must supply `retry_of` (retained primary attempt ID) and `retry_reason` (plain text). Missing or conflicting provenance stops the build.

**Save / load** exports or imports choices. Import validates the experiment, view type, plan SHA and every selected attempt ID/image SHA before changing any state. Unknown approval/ranking fields, malformed responses, overlong notes and stale image bindings are rejected atomically. Notes are limited to 4,000 characters. Browser storage is scoped to each exact dataset. Comparison and sequence choices use separate scopes, so adding the later sequence does not reset the comparison dataset's choices. Keep an exported JSON as the durable handoff; comparison lineups and currently displayed tabs are temporary viewing state.

The sequence defaults to **Read story**, hiding each panel’s response footer and repair tools while keeping the art, dialogue and global Save / load controls available. **Review panels** reveals those tools. Switching views or reloading does not modify saved choices; a fresh page returns to Read story.

The sequence uses the same six frozen panels and exact copy across three transparently provisional styles. Dialogue and SFX are editable HTML/CSS/source JSON, separate from the PNG art, and displayed below each panel. No unreviewed balloon bounds are inferred from earlier images. The scene agent intentionally supplied no initial overlays. Owner response controls remain optional so the first reading stays focused on art and dialogue.

## Build contract

Lead-owned inputs are all in `production/visual-refinement/`:

- `comparison-plan.json`: `RefinementComparisonPlan/1`, experiment ID, nine styles/references, two characters, 18 controlled IDs `<style>-A/B`, and X1/X2 exploratory entries.
- `candidates.json`: `{candidates:[{id,attempt_id,path,sha256,width,height,status}]}`. Selected status is `reviewable-unaccepted`. `selected.json` maps `{selected:{entryID:attemptID}}`.
- `sequence-plan.json`: experiment ID, `provisional_styles` (empty before selection or three styles), six `panels` with exact `copy:[{id,speaker,text,kind}]` and `target_height_at392`.
- `sequence-candidates.json` and `sequence-selected.json`: the same candidate contracts with IDs `<style>-P01` through `<style>-P06`.
- Optional `sequence-review-notes.json`: the same `RefinementReviewNotes/1` schema with `entries` bound to sequence candidates. Optional `routes:[{style_id,observations,source_bindings:{id:{attempt_id,sha256}}}]` must bind all six selected images in each route. Route observations remain a separate collapsed disclosure; panel observations appear only in Review panels. Neither sets owner choices. Footer report links activate when new-namespace START_HERE.md and RESULTS.md exist.
- Optional `review-notes.json`: `RefinementReviewNotes/1`, experiment ID and `entries:{id:{attempt_id,sha256,observations:[plain text]}}`. Every note must match the currently selected image; stale notes stop the build. Adding AI observations does not change the source-bound owner-choice scope.

The builder validates every selected PNG signature, dimensions, SHA, namespace and ID, plus source style-reference hashes. It writes only this new reader's `comparison-data.{json,js}` and `sequence-data.{json,js}`. Pending art has no substituted candidate. No plan, selection, preference, or art file is mutated by a build.

```sh
python research/visual-refinement/reader/build_reader.py
python research/visual-refinement/reader/build_reader.py --require-comparison --require-sequence
node research/visual-refinement/reader/browser_qa.mjs --require-complete
```

The final flags require 20 actual selected comparison boards and 18 actual sequence panels. Without them, the UI and QA explicitly report progress/missing art and do not claim completion.

## Browser QA

The task owns Chromium CDP9367 and the profile under `research/visual-refinement/reader/.scratch/browser/profile`. The helper creates a fresh page, captures 390×844, 1024×768 and 1440×1000, and writes only the new namespace. Override the port with `REFINEMENT_QA_PORT`. Screenshots and actual JSON download/import files live in that scratch directory. `browser-qa.json` binds the exact reader code/data and lists current completeness.

Checks include actual full-image display, explicit pending states, A/B comparisons, phone stacking, fit/native zoom, Escape, independent responses, real file download/import/reload, source hashes, mismatched-import atomicity and a deliberate missing-image simulation. Its expected missing-file browser error is recorded separately from unexpected errors. QA restores original preference values and does not write owner votes to production records. Source/hash/geometry checks do not establish artistic quality or owner comfort.

Focused final observations/report-link integration can be checked with `node research/visual-refinement/reader/notes_qa.mjs`. This preserves the complete art/UI receipt and binds any later note-only code/data changes separately.
