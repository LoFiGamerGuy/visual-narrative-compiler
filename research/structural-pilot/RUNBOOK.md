# Use the delivered workflow

Run commands from this isolated checkout. Python 3 and Node are enough to build the readers. The delivered local assets are already present; a fresh clone needs restoration from the asset bundle described below.

```bash
python research/structural-pilot/build_reader.py
python research/structural-pilot/build_reader.py --correction --input production/structural-pilot/reader-patches/CF-reader-input.json
python research/structural-pilot/build_comparison.py
python -m http.server 9360 --bind 127.0.0.1
```

Open `http://127.0.0.1:9360/docs/research/structural-pilot/correction-reader/index.html`. The corrected proof is the default. The SC reader preserves baseline B, generated G and fixed-layer S; neutral labels reduce provenance distraction but do not establish a blinded human study. All images remain unaccepted.

## Persist a lettering edit

Choose **Edit / review**, select a panel, change the balloon or tail, and export a draft JSON. Put the draft inside `production/structural-pilot/drafts/` in this checkout. Preview validation before application:

```bash
python research/structural-pilot/apply_reader_draft.py check production/structural-pilot/drafts/my-draft.json --correction
python research/structural-pilot/apply_reader_draft.py apply production/structural-pilot/drafts/my-draft.json --correction
```

Omit `--correction` for the SC reader. The command checks current art, plan and selected-input hashes, exact original copy, finite geometry, font minima and protected surrounding panels. It saves immutable before/after/draft/patch history, updates only the selected reader input and rebuilds. Stale drafts are rejected; export a fresh one after another edit changes the input. Empty changes do not mutate the input. Browser notes remain observations and cannot approve the underlying art. This scoped bridge does not import invented composite candidate IDs into the raw image-generation ledger.

## Edit art and controls

Open the selected external-reference SVGs linked in [START_HERE](START_HERE.md) with their neighboring raster sources available. Conventional repair recipes expose source clones, masks, transforms, drawn contacts and motion paths. Save every new art version under a new path; never replace an existing candidate or bound SVG/spec. The frozen SC and CF generation/correction budgets are closed. New art experiments require a new explicit hypothesis and scope, not another retry under a renamed old allowance.

The [Blender control README](../../production/structural-pilot/control/README.md) explains the seven scenes, layer order, anatomical-side metadata and versioned rebuild. v8 is the frozen raster-conditioning source. v9 only explores a clearer P12 fragment separation. Geometry checks do not guarantee that a final drawing preserves those relationships.

`production/structural-pilot/compose_svg.py` constructs a new source-bound SVG from a new explicit spec. `render_svg.mjs source.svg new-output.png PORT` exports it using a running Chromium CDP instance. They preserve existing outputs. The included `qa/cdp.mjs` startup helper is specific to this machine's existing Chromium and library locations; on another machine use its own Chromium with a task-owned profile and remote debugging port. No environment or global browser setup is changed by the reader build.

## Checks

```bash
python -m unittest discover -s research/structural-pilot -p 'test_apply_reader_draft.py'
python -B production/structural-pilot/control/validate_control.py
node research/structural-pilot/qa/cdp.mjs start 9351
node docs/research/structural-pilot/reader/qa.mjs
node docs/research/structural-pilot/reader/qa.mjs --correction
```

Browser QA covers 390×844, 1024×768 and 1440×1000; inspect actual screenshots as well as JSON results. `READER_QA_PORT` selects another already running CDP port. The immutable actual-art reviews explain semantic/artistic limitations which passing code cannot settle.

## Asset restoration

The local archive and its manifest are under `research/structural-pilot/asset-bundle/`. Follow that directory's README to verify and restore in a fresh checkout. It includes the original generated assets, control renders/Blender files, all finishing rasters and preserved inline-raster originals, plus the baseline context needed to rebuild. Runtime browser profiles and dependencies are excluded. The archive is local and ignored; Git carries recipes and hashes, not generated raster payloads. No public asset upload is part of this delivery.
