# Combat exploration reader

This isolated offline reader displays18 independent adult combat character alternatives: C1/C2 in styles01/02/05/06/13/15/17/18/19. Each3:2 board is one adult in two views. The original nine starred boards are reference-only. No default preference, ranking, production approval or assumed character pair is created.

Open `docs/combat-exploration/index.html` after the lead runs the managed builder. All/style/shortlist browsing,2–3 board comparisons, uncropped native zoom and retained attempt histories use local files only. Each character has independent Character, Drawing style, Weapon and Power appeal choices, plus comfort, a note and shortlist membership. Clicking an active appeal clears it. Shortlisting does not set any appeal.

## Inputs and build

`production/combat-exploration/combat-plan.json` uses `CombatExplorationPlan/1`, an experiment ID, nine styles and18 entries with `id`, `style_id`, `character_id`, `title`, adult integer `age`, `caption`, and named/described `weapon` and `power` objects. Optional `progression` strings appear in a collapsed Possible power growth disclosure. Extra frozen prompt fields remain source data. Visible drawing labels use the first semicolon-delimited phrase; full frozen descriptions remain intact. `references.json` is the nine original-anchor array. `candidates.json` retains native PNG path/hash/dimensions and attempt identity; `selected.json` maps each entry to its displayed attempt. Retries require a retained `retry_of`, `retry_reason` and exact local call record. Optional `review-notes.json` observations are bound to the selected attempt and image SHA and appear separately in collapsed disclosures.

```sh
python research/combat-exploration/reader/build_reader.py
python research/combat-exploration/reader/build_reader.py --require-complete
```

The first command allows explicit missing-board states. The strict command requires all18 real selected boards. Neither changes source plans, selections or art. All assets stay inside `production/combat-exploration`; no previous namespace is written.

Choice files use `CombatExplorationChoices/1`. Their experiment, plan SHA and complete ordered18-entry attempt/image-SHA list must match. Imports validate all fields before changing choices and reject unknown approval/score fields. Source changes have a separate localStorage dataset, with blank defaults. Notes and call-history additions do not silently move votes between sources. A failed image load disables new edits to that entry while preserving existing choices.

## Reproducible checks

```sh
python -m unittest discover -s research/combat-exploration/reader -p test_builder.py
node research/combat-exploration/reader/test_preferences.mjs
node research/combat-exploration/reader/browser_qa.mjs
node research/combat-exploration/reader/browser_qa.mjs --require-complete
node research/combat-exploration/reader/final_qa.mjs
node research/combat-exploration/reader/capture_phone.mjs
node research/combat-exploration/reader/capture_history.mjs
```

Browser commands use task-owned CDP9378. The main check uses390×844,1024×768,1440×1000, actual local image decoding, source hashes, responsive comparisons, native zoom, nested Escape, blank defaults, independent preferences, real download/file-input import, atomic rejection, missing-source behavior and restored original choices. Phone captures can take specific entry IDs as arguments; history captures default to retries or accept exact attempt IDs, without changing selected images; they never change choices or production selections. PNGs and hash-bound receipts go under this reader's `phone-captures` directory.

For a restored checkout, use the already-frozen helper with explicit output outside frozen source:

```sh
node research/combat-exploration/reader/browser_qa.mjs --smoke --root /absolute/restored/root --out /absolute/ignored/evidence --port 9378
```

Smoke checks require18 boards, use390/1440, decode all displayed and retained images, inspect notes/anchors/links and keep owner choices unchanged. Launch Chromium only with a profile under this study's `.scratch`; do not reuse or stop another task's browser. Disposable test/download files remain under the chosen output's `.scratch`.
