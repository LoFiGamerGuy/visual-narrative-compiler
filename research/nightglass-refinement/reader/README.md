# Nightglass refinement reader

This isolated offline gallery contains24 new source-bound studies: four texture pairs T01–T04, six scenes S01–S06, four characters C01–C04, three equipment studies G01–G03, W01 wildlife, M01/M02 monsters and four abilities A01–A04. Full scenes opens by default. Texture pairs presents matched before/after images side by side on desktop and stacked on phone, with native access to both sides.

The before sources are fixed: T01←WC S01, T02←WC S06, T03←WC C01 and T04←WC M01. The previous-world manifest/data bind their exact original attempts and image hashes. Missing new images are explicit; before art is never used as a substitute after image.

Every new choice begins blank. Texture pairs have independent preferred version (Before/After/Unsure/Neither), overall, drawing, texture, key-element preservation and comfort responses. Choosing a version does not set another rating. Other categories retain their own dimensions and add texture. N/A is explicit `na`, distinct from unanswered `null`. Notes and shortlist membership remain independent. No old shortlist populates the new one.

Earlier CE choices are a separate18-image read-only table view with the exact preserved export download. The previous WC round is a separate24-image read-only view with verbatim global feedback; no WC per-image ratings were supplied or invented. All nine original reference boards remain separate benchmarks.

## Managed inputs and build

The lead owns `production/nightglass-refinement/refinement-plan.json` (`NightglassRefinementPlan/1`), candidates/selected/calls, references, preserved sources and source-bound review notes. The builder writes only the new docs `data.json`/`data.js`. The copied CE manifest/validation intentionally retain `WorldCombatPreviousSources/1` and `WorldCombatPreviousValidation/1` schemas. The previous-world manifest uses `NightglassRefinementPreviousWorld/1`; owner feedback is `production/nightglass-refinement/owner-feedback.json`.

```sh
python research/nightglass-refinement/reader/build_reader.py
python research/nightglass-refinement/reader/build_reader.py --require-complete
```

During generation, the lead runs managed builds. Strict completion requires24 real selected3:2 PNGs. The builder verifies native bytes, dimensions, paths, retry/call evidence, previous source bindings and frozen T before-ID mapping.

`NightglassRefinementChoices/1` uses exact category-specific rating keys plus comfort, note, shortlist and `preferred_version`. Non-T version preference must remain null. Every one of the24 binding records has six fixed fields: `id`, `attempt_id`, `sha256`, `before_id`, `before_attempt_id`, `before_sha256`; non-T before fields are null. Both sides of each pair participate in dataset identity. Changing either side requires a new blank dataset, and stale imports reject atomically. Previous exports cannot be imported into this round.

## Checks and actual captures

```sh
python -m unittest discover -s research/nightglass-refinement/reader -p test_builder.py
node research/nightglass-refinement/reader/test_preferences.mjs
node research/nightglass-refinement/reader/browser_qa.mjs
node research/nightglass-refinement/reader/browser_qa.mjs --require-complete
node research/nightglass-refinement/reader/final_details_qa.mjs
node research/nightglass-refinement/reader/capture_phone.mjs
node research/nightglass-refinement/reader/capture_history.mjs
```

The22 builder tests and20 atomic preference rejection cases use disposable fixtures only in this reader's `.scratch`. Actual browser checks use the task-owned CDP9380 and profile in `reader/.scratch/browser`, at390×844,1024×768 and1440×1000. They cover new pairs, prior-round isolation, exact downloads, category views, comparisons, source/native history, ratings/imports, missing sources, notes and blank restored choices. Phone captures accept entry IDs and record both complete pair images where applicable. Images and hash receipts are durable under `phone-captures`.

For portable or committed-checkout QA, write evidence only to an explicit ignored output:

```sh
node research/nightglass-refinement/reader/browser_qa.mjs --smoke --root /absolute/restored/root --out /absolute/ignored/evidence --port 9380
```

Never run old scripts that write their original namespaces, or reuse/stop another task's browser.
