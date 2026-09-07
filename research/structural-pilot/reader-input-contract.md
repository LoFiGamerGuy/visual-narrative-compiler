The builder reads `production/structural-pilot/reader-input.json` and creates data and hash-verified local raster copies for `docs/research/structural-pilot/reader/index.html`. Run `python research/structural-pilot/build_reader.py` in this checkout. It touches only the new reader output directory. Existing reader/editor code is reused as an isolated frontend copy.

The input declares `experiment_id`, `plan_path`, `selected_panels` exactly `["P09","P11","P13","P14"]`, and `routes` exactly S then G. Each route has `id`, `label_provenance`, and `panels`. The baseline is implicit. X/Y/Z labels derive deterministically from experiment ID plus route ID; input `label_neutral` does not override that mapping. Optional `baseline_path` defaults to the inherited sequence reader JSON in this checkout.

Example replacement entry inside a route's `panels` object:

```json
{
  "P11": {
    "candidate_id": "SC-S-P11-A1",
    "path": "production/structural-pilot/control/final/P11.png",
    "sha256": "EXACT_PNG_SHA256",
    "lettering": [{
      "id": "P11-L01", "kind": "ui", "speaker": "",
      "text": "AIR BRAKE · PULSE 2 → 1", "shape": "rounded",
      "x": 0.06, "y": 0.035, "w": 0.65, "h": 0.1,
      "font_size": 13.5, "tail": null
    }],
    "protected_regions": [],
    "source_links": [{
      "label": "Editable layered source",
      "path": "production/structural-pilot/control/final/P11.svg"
    }]
  }
}
```

This is an interface example, not an image-grounded approved lettering position. Paths resolve relative to this checkout; final displayed art must be PNG. The supplied PNG SHA must match actual bytes. Editable links are independently hash-bound in the generated manifest; an optional supplied `sha256` is checked.

P09/P13 are silent and require `lettering: []`. P14 requires the exact ordered transcript `ODO: Steady.` then `NERA: I am.`. Every replacement supplies fresh lettering explicitly; prior protected regions and prior semantic observations are not transferred to new art. Ten context panels retain their original art/copy/canvas/lettering. A route missing a screened panel shows a visible missing candidate rather than substituting baseline art.

The default continuous reader is compact and art-first. Review/edit retains the existing SVG lettering editor and hash-bound `SequenceReviewDraft/1` import/export, adding route and experiment IDs. Switching routes preserves draft edits in the tab; export each changed route to retain them. Matched comparison uses the same planned 390px-wide canvas for each version, with uncropped art and separate lettering. Desktop rows wrap when three canonical-width panels will not fit.

Reader drafts round-trip through this reader. They contain all fourteen context panels; the new attempt-ledger plan contains only four screened panels, and derived S/CF composition IDs are separate from registered raw generation IDs. Consequently these full-reader drafts are not direct inputs to the existing backend `import-draft` command. The small `apply_reader_draft.py` command described below persists layout edits into the selected new reader input without changing backend attempts or semantic observations.

Neutral labels hide provenance, candidate IDs, source links and acceptance blockers; frozen requirements remain available on request. This is label masking, not verified blinding or human review. Reveal provenance to access editable sources. All versions remain draft-unaccepted. `source-bindings.json` reports exact source/display hashes; these establish file identity, not semantic correctness or artistic quality.

The separately frozen `CF-20260907-02` conventional correction proof has a separate output directory and explicit provenance labels. Build it with:

```sh
python research/structural-pilot/build_reader.py --correction --input production/structural-pilot/reader-patches/CF-reader-input.json
```

This input uses the same envelope but `plan_path` points to `correction-experiment.json` and routes are exactly G then CF. G must contain all four exact source hashes frozen in that correction experiment. CF carries P14 unchanged and every edited entry supplies `source_candidate_sha256` matching its frozen generated source. An absent CF correction remains visibly missing. No new route is added to the original B/S/G screen. The correction reader labels P14 as an unchanged generated reference and makes no conventional correction claim for it.

Local Chromium browser QA runs with `node docs/research/structural-pilot/reader/qa.mjs`; append `--correction` for the separate correction reader. Use the task-owned browser on port 9351, or set `READER_QA_PORT` to another isolated browser. Receipts and screenshots go to `research/structural-pilot/.scratch/reader-browser/`. Run final QA after the selected artwork and layouts are integrated; earlier receipts explicitly list missing panels and bind the input hash.

To retain a lettering edit in the active workflow, open the complete current reader, select its version, choose **Edit lettering**, make the edit, and use **Export review JSON**. Place that export inside this checkout, for example in `production/structural-pilot/layout-drafts/`. Preview the exact proposed patch, then apply and rebuild:

```sh
python research/structural-pilot/apply_reader_draft.py check production/structural-pilot/layout-drafts/my-draft.json --correction
python research/structural-pilot/apply_reader_draft.py apply production/structural-pilot/layout-drafts/my-draft.json --correction
```

Omit `--correction` for S/G in the original screen. The default selected inputs are `reader-input.json` for S/G and `reader-patches/CF-reader-input.json` for G/CF. An explicit `--input` must name a selected `*reader-input.json` file inside the new production namespace; history snapshots and prior namespaces are never mutable targets. The preserved B version is read-only through this command.

The command checks experiment, route, frozen plan and current selected-input hash; all fourteen exact candidate IDs/hashes; exact ordered copy; finite normalized geometry; and canonical font floors of14px dialogue,12px UI,6px SFX. Ten surrounding context layouts are protected. Screened lettering/regions can change; CF P14 permits lettering only. Acceptance/verified-identity fields are rejected. Browser notes remain unverified data in the saved draft snapshot and never enter semantic records.

Before applying, the command saves exact prior/next input bytes, the exact browser export and the concrete patch in a new UTC/hash-named `layout-history/` directory. It refuses to overwrite snapshots and binds their hashes; this is local tool-enforced history, not an externally signed record. It then replaces only the selected new input and rebuilds its reader. Reload the rebuilt reader before the next export: an export bound to the older input is rejected as stale. To deliberately restore an older layout, import that hash-compatible old layout into the current reader and export it again, then check/apply it as another preserved version.

The delivered demonstration used this exact workflow to move Nera's P14 balloon and lengthen its visible tail, then matched the layout in both G source views. Independent actual-phone review confirmed attribution improved without occluding faces or hands, so the new layout was retained. Prior versions remain preserved. `reader/draft-application-qa.json` records the demonstration and validation tests. The command validates structure and source identity; rendered lettering and image semantics still require actual-art review.
