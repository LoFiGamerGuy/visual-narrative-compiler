# Impact clarity offline reader

This reader presents sixteen independent studies in three groups: eight Core, four Radical and four Other styles. Gallery is the default; each group has its own filter. Read all keeps captions off and has adjustable gaps. Pair actions use only explicit frozen paired_ids, with complete images at matched widths. Preferences begin blank and are bound to the exact experiment, plan and ordered selected artwork hashes.

Parent-managed build:

```sh
python3 research/impact-clarity/reader/build_reader.py
python3 research/impact-clarity/reader/build_reader.py --require-complete
```

Input: production/impact-clarity/plan.json (ImpactClarityPlan/1), candidates.json, selected.json, calls/<attempt>.json and optional review-notes.json (ImpactClarityReviewNotes/1). Root owns all production files and build invocations. Cards require id/title/category/group/scale/subjects/caption; references and paired_ids are explicit lists. Power may be null or have name/description/limitation/growth. Current or exact preserved plan-history sources bind calls. Original CE choice exports remain separate read-only downloads.

Validation:

```sh
python3 research/impact-clarity/reader/test_builder.py
node research/impact-clarity/reader/test_preferences.mjs
```

Browser helpers use task-owned CDP9383. All source code and QA writes stay in docs/impact-clarity and research/impact-clarity/reader. No generation or artwork mutation is performed by the reader.

Actual browser QA and source-bound captures (run only when the parent has released a stable managed dataset):

```sh
node research/impact-clarity/reader/browser_qa.mjs --port 9383
node research/impact-clarity/reader/browser_qa.mjs --require-complete --port 9383
node research/impact-clarity/reader/capture_phone.mjs M01 M02
node research/impact-clarity/reader/capture_history.mjs M01-P M01-R1
node research/impact-clarity/reader/capture_strip.mjs M01-P M01-R1
```

Portable runs use the same full helper with `--root /absolute/restored/root --out /absolute/ignored/evidence --require-complete --port 9383`. Output override includes all screenshots, receipts and download scratch; frozen source and production inputs remain read-only. `--smoke` is available for a narrower 390/1440 check, but the final delivery calls for the full three-size run.

Scope amendment: the current plan has sixteen entries, adding Y01–Y04 under category `style`, group `comparison` and optional visible `drawing_direction`. The Other styles filter is separate from Core and Radical. Original twelve-entry frozen plan files remain valid sources for earlier call hashes; the current final reader requires all sixteen images. The builder adds a supporting local `combat-references/index.html` link when that separately owned board exists.

Paired and style-specific captures:

```sh
node research/impact-clarity/reader/capture_pairs.mjs X01 X02 X03 X04
node research/impact-clarity/reader/capture_styles.mjs
node research/impact-clarity/reader/linked_board_qa.mjs --port 9383
```

The linked-board check verifies all sixteen exact observation bindings, the three report links, actual offline navigation to the separate reference board and back, local excerpt loading at all three sizes, and unchanged blank preferences in both interfaces. It also accepts `--root` and `--out` for portable checks without source writes.
