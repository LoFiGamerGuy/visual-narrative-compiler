# World & combat offline reader

This new namespace displays24 distinct source-bound cards: six full scenes S01–S06, six characters C01–C06, four equipment studies G01–G04, wildlife W01/W02, monsters M01/M02 and abilities A01–A04. The six full scenes open by default in a wide single-column gallery. Category/all/shortlist modes,2–3 image comparisons, native zoom and links to related new studies never create ratings. Captions and optional combat roles are visible below art; proposed power growth and separate AI technical observations are collapsed.

All new choices start blank. Dimensions vary by category; each supports Like/Dislike/Unsure/N/A. N/A is the explicit `na` value; unanswered remains `null`. Comfort, notes and shortlist membership are independent. Clicking an active response clears it. No ranking or automatic cast/world selection is inferred.

The previous combat-character round appears in a separate read-only modal with18 source-bound images and exact response tables. Its download points directly to the preserved JSON bytes. Previous shortlists never populate the new shortlist, and the new importer rejects the old schema. All nine original reference boards remain separate benchmarks.

## Input and managed build

The lead owns `production/world-combat/world-combat-plan.json` (`WorldCombatPlan/1`), candidates/selected/calls, references, previous sources and source-bound review notes. The reader builder only writes `docs/world-combat/data.json` and `data.js`. It verifies the fixed24 IDs/categories, native3:2 PNG bytes/dimensions/hash, declared styles, local new-namespace paths, retained retry provenance and exact previous export/data/plan/image bindings against `research/world-combat/previous-validation.json`.

```sh
python research/world-combat/reader/build_reader.py
python research/world-combat/reader/build_reader.py --require-complete
```

Only the lead runs managed builds during generation. Pending cards explicitly lack art and cannot be rated. No reference replaces missing generated art. The strict build requires24 actual selected native images.

Exports use `WorldCombatChoices/1` with exact experiment, plan hash, complete ordered24-entry attempt/image-SHA bindings and category-specific rating keys. Validation completes before mutation; stale, partial, extra-dimension or approval-bearing imports fail atomically. Changed selected sources create a separate blank localStorage dataset. A failed image load prevents new responses for that card while preserving previous choices.

## Checks and captures

```sh
python -m unittest discover -s research/world-combat/reader -p test_builder.py
node research/world-combat/reader/test_preferences.mjs
node research/world-combat/reader/browser_qa.mjs
node research/world-combat/reader/browser_qa.mjs --require-complete
node research/world-combat/reader/final_details_qa.mjs
node research/world-combat/reader/capture_phone.mjs
node research/world-combat/reader/capture_history.mjs
```

Browser commands use this task's Chromium CDP9379 and a profile inside `reader/.scratch/browser`. Actual checks cover390×844,1024×768 and1440×1000, source decoding/hashes, scene defaults, category dimensions, related views, comparisons/zoom, exact previous tables and downloaded bytes, old/new choice isolation, source-bound export/import, missing-source behavior and blank restored defaults. The18 builder tests and17 preference-rejection cases use disposable fixtures only under the new reader's `.scratch`.

Phone captures accept specific new card IDs; history captures accept exact attempt IDs or default to retries. Both preserve production selections and preferences, retain complete native-ratio images at actual390px width, and write durable image/call/dataset/code/screenshot receipts under `phone-captures`.

For archive or committed-checkout verification, write only to an explicit ignored output directory:

```sh
node research/world-combat/reader/browser_qa.mjs --smoke --root /absolute/restored/root --out /absolute/ignored/evidence --port 9379
```

Smoke uses390/1440, requires24 images and retains existing preferences. Never run previous namespace scripts that write their original outputs; never reuse or stop another task's browser.
