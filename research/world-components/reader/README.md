# Offline world-component reader

Open `docs/world-components/index.html`. All styles and components live in the new world-components namespace. The reader uses local HTML, CSS, JavaScript and native PNGs, with no server, external font or network script.

## Owner workflow

Browse **By style kit** for six independent studies in one world, **By component** for one category across nine styles, or **Mix tray** for parts collected across styles. C1/C2 are character alternatives, not an assumed pair. Each card contains one image; G1 may contain at most three tools, with names and functions below its image. Kit world rules, drawing rules and possible conflicts remain collapsed exploratory context.

Every component has its own Keep / Reject / Unsure response and independent Yes / No / Unsure comfort response. All start blank. Clicking an active response clears it. Notes and mix membership are independent: adding a part to the mix tray does not automatically keep it, create a pair, or declare canon. The tray count is only the number of collected items, never a score or ranking.

The nine earlier stars identify original anchors. **Original anchor** opens the source board without new-image choice controls. The two or three component comparison shows complete images at matched viewing widths; phone comparisons stack. Tap any new image to fit the complete image or inspect native pixels. All native paths are local.

**Image history & repair proof** appears when multiple attempts are retained for a component. It shows every retained PNG and the displayed attempt, with attempt IDs, hashes, native links, hashed call records and any stated correction target. Prompt/reference inputs may differ. This history view has no choice controls and does not claim repair success.

AI technical observations remain a separate collapsed disclosure. They never set owner responses. Missing candidates use explicit placeholders; missing source files show an error and disable new choices while retaining previously stored choices.

Save / load exports or imports `WorldComponentChoices/1` JSON. It binds the exact experiment, frozen plan, all54 IDs, selected attempt IDs and source SHA values. Unknown canon/score fields, stale bindings and malformed values are rejected atomically. Browser storage is scoped to the exact dataset; replacing a selected attempt starts a separate blank scope. Keep an exported JSON for a durable handoff.

Optional viewing deep links: `index.html?mode=component&category=E1`, `index.html?mode=kit&style=18`, or `index.html?mode=mix`. These are viewing state, not preferences.

## Input contract and checks

Lead-owned `production/world-components/` inputs:

- `kit-plan.json`: `WorldComponentPlan/1`, experiment ID, nine styles, six categories, and54 entries `{id,style_id,category_id,title,caption}`. Optional gear `items:[{name,function}]` is capped at3. Optional style `world_title`, `world_rule`, `visual_rules`, `possible_conflict` supply short collapsed context.
- `references.json`: nine `{id,path,sha256}` original anchor bindings.
- `candidates.json`: `{candidates:[{id,attempt_id,path,sha256,width,height,status:'reviewable-unaccepted'}]}` retaining all attempts.
- `selected.json`: `{selected:{componentID:attemptID}}`.
- Existing `calls/<attempt_id>.json`; retries supply `retry_of` and `retry_reason`. History requires their exact call records and retained source attempts.
- Optional `review-notes.json`: `WorldComponentReviewNotes/1`, experiment ID, `entries:{id:{attempt_id,sha256,observations:[strings]}}`. Notes must match current selected sources; adding notes does not reset owner-choice scope.

`display-text-overrides.json` is an auditable reader-only mapping from exact frozen caption/function text to clean displayed descriptions. It removes generation instructions and unsupported visibility assertions, retains the original fields, and fails if the frozen text no longer matches. The override file is separately hashed; display-only changes do not reset source-bound choices.

The builder writes only this reader’s `data.json` and `data.js`. It verifies PNG signatures, declared dimensions, new-namespace paths, SHA values, selected IDs/status, original anchors, retained attempts and notes. It never changes plans, selections, source art or owner choices.

```sh
python3 research/world-components/reader/build_reader.py
python3 research/world-components/reader/build_reader.py --require-complete
python3 research/world-components/reader/test_builder.py
node research/world-components/reader/test_preferences.mjs
node research/world-components/reader/browser_qa.mjs --require-complete
```

Early builds may contain0–53 real images with visible pending states; the final flag requires all54. No anchor or prior experiment image substitutes for missing new art. Disposable test fixtures stay under this reader’s scratch directory and are never published as artwork.

Task-owned Chromium uses CDP9377 and `.scratch/browser/profile`. Browser checks create fresh pages, capture390×844,1024×768 and1440×1000, and write only this reader’s evidence/scratch. `WORLD_COMPONENT_QA_PORT` can override the port. The helper checks all nine kits and six category views, native anchors, comparison/history views, independent choices, cross-style mix collection, keyboard activation, actual download/import/reload, atomic invalid imports, exact source hashes and intentional missing-file behavior. Expected missing-file browser errors are recorded separately. No UI pass establishes artistic quality or owner comfort.
